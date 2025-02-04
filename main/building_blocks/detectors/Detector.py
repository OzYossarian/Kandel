from typing import List, Tuple

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Coordinates
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.utils.NiceRepr import NiceRepr
from main.utils.utils import modulo_duplicates, coords_mid


TimedCheck = Tuple[int, Check]


class Detector(NiceRepr):
    """A set of checks whose measurement outcomes' product should be
    deterministic in the absence of any noise."""

    def __init__(
            self,
            timed_checks: List[TimedCheck], end: int,
            anchor: Coordinates = None):
        """Detector constructor

        Args:
            timed_checks:
                the set of timed checks that make up the detector. A 'timed
                check' is an (int, Check) tuple, where the int is the number
                of rounds before the `end` round this check is measured at.
                # TODO - link to an example in the documentation.
            end:
                The first round (modulo schedule length) by which ALL of the checks
                in the stabilizer will have been measured.
            anchor: 
                Coordinates at which to 'anchor' this stabilizer. If None,
                defaults to the midpoint of the anchors of all checks
                involved.
        """
        self._assert_timed_checks_valid(timed_checks)

        self.timed_checks = timed_checks
        self.final_checks = [check for t, check in self.timed_checks if t == 0]
        self.product = self.timed_checks_product(self.timed_checks)

        if anchor is None:
            check_anchors = [check.anchor for _, check in self.timed_checks]
            anchor = coords_mid(*check_anchors)
        self.anchor = anchor

        # Including the same check twice in a detector does nothing - note
        # down the checks modulo pairs of duplicates.
        self.timed_checks_mod_2 = modulo_duplicates(self.timed_checks, 2)

        # Note down when the first and last checks were measured
        first_check_rounds_ago = min(
            rounds_ago for rounds_ago, check in self.timed_checks)
        self.start = end + first_check_rounds_ago
        self.end = end

        super().__init__(['product.word', 'end', 'timed_checks'])

    def checks_at_or_before_(self, semi_relative_round: int, absolute_round: int):
        zero = semi_relative_round - absolute_round
        checks = [
            (t, check) for t, check in self.timed_checks
            if zero <= t <= semi_relative_round]
        return checks

    def is_open(self, semi_relative_round: int) -> bool:
        """
        Whether this detector is 'open' immediately after the given semi-relative round.
        An open detector is one where not all of the checks in the detector have actually been measured yet.
        e.g. measuring ZZ in consecutive rounds is a detector,
        and immediately after the first check the detector is 'open',
        since the second check hasn't been performed yet.

        We say 'semi-relative' round, because the round may be the actual relative round,
        (i.e. the round number modulo schedule length, so it's in [0, schedule_length)),
        or the relative round minus k*schedule_length for some integer k.
        This is to account for detectors that are so tall they span multiple schedule layers.

        Args:
            semi_relative_round:
                The round that has just been measured, modulo schedule length,
                and perhaps with an integer multiple of schedule length subtracted (see above).
        """
        return self.start <= semi_relative_round < self.end


    @staticmethod
    def timed_checks_product(timed_checks: List[TimedCheck]):
        # Pauli multiplication is not commutative so order matters.
        # TODO - this is ambiguous if non-commuting Paulis appear in the same
        #  round! e.g. if a qubit is involved in an XX...X check and YY...Y
        #  check in the same round, it's ambiguous as to whether this product
        #  should have an XY or YX contribution from this qubit.
        timed_checks = sorted(
            timed_checks, key=lambda timed_check: -timed_check[0])
        paulis = [
            pauli for (_, check) in timed_checks
            for pauli in check.paulis.values()]
        product = PauliProduct(paulis)
        return product

    @staticmethod
    def _assert_timed_checks_valid(timed_checks: List[TimedCheck]):
        if len(timed_checks) == 0:
            raise ValueError("Detector must contain at least one check!")
        if not any([t == 0 for t, check in timed_checks]):
            raise ValueError(
                "At least one timed check must have time component 0 - i.e. "
                "it must be measured in the detector's `end` round. "
                "(Otherwise the round specified as the `end` is not really "
                f"the end!). The given timed checks are: {timed_checks}")
        if any([t > 0 for t, check in timed_checks]):
            raise ValueError(
                "No timed check can have time component > 0, because this "
                "would mean it's measured after the detector's `end` round. "
                f"The given timed checks are: {timed_checks}")

        dimensions = {check.dimension for t, check in timed_checks}
        if len(dimensions) > 1:
            raise ValueError(
                f"All checks in a detector must have the same dimension. "
                f"Instead, found dimensions {dimensions}. "
                f"The given timed checks are: {timed_checks}.")
        all_tuple_coords = all([
            check.has_tuple_coords for t, check in timed_checks])
        all_non_tuple_coords = all([
            not check.has_tuple_coords for t, check in timed_checks])
        if not (all_tuple_coords or all_non_tuple_coords):
            raise ValueError(
                "Can't mix tuple and non-tuple coordinates!"
                f"The given timed checks are: {timed_checks}.")

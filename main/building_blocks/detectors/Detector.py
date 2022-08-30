from typing import List, Tuple

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Coordinates
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.utils.NiceRepr import NiceRepr
from main.utils.utils import modulo_duplicates, coords_mid


TimedCheck = Tuple[int, Check]


class Detector(NiceRepr):
    """A set of checks whose Pauli product should be deterministic in the absence of any noise."""
    
    def __init__(
            self,
            timed_checks: List[TimedCheck], end: int,
            anchor: Coordinates = None):
        """Detector constructor

        Args:
            timed_checks:
                The set of timed checks that make up the detector. A 'timed
                check' is an (int, Check) tuple, where the int is the number of rounds
                before the `end` round this check is measured at.
                # TODO - link to an example in the documentation.
            end:
                The first round (modulo schedule length) by which ALL of the checks
                in the stabilizer will have been measured.
            anchor: 
                Coordinates at which to 'anchor' this stabilizer. If None,
                defaults to the midpoint of the anchors of all checks
                involved.
        """
        self.timed_checks = timed_checks
        self.final_slice = [check for t, check in self.timed_checks if t == 0]

        self.product = self.timed_checks_product(self.timed_checks)
        if self.product.word.sign not in [1, -1]:
            sign = self.product.word.sign
            raise ValueError(
                f"Can't create a Detector whose product has sign {sign}. Sign "
                f"must instead be 1 or -1. Detector has timed checks "
                f"{self.timed_checks}.")

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

        super().__init__(['product.word', 'timed_checks'])

    @staticmethod
    def timed_checks_product(timed_checks: List[TimedCheck]):
        # Pauli multiplication is not commutative so order matters.
        timed_checks = sorted(
            timed_checks, key=lambda timed_check: -timed_check[0])
        paulis = [
            pauli for (_, check) in timed_checks
            for pauli in check.paulis.values()]
        product = PauliProduct(paulis)
        return product

from __future__ import annotations
from typing import List, Tuple

from main.building_blocks.Qubit import Coordinates
from main.building_blocks.detectors.Detector import Detector, TimedCheck


class Drum(Detector):
    def __init__(
            self, floor: List[TimedCheck], lid: List[TimedCheck], end: int,
            anchor: Coordinates = None):
        """Detector with a drum shape.

        Specific type of Detector, where the same Pauli product (up to +/-
        sign) is measured across different rounds, and is not destabilized
        in the meantime. Comparing these two outcomes should thus give a
        deterministic result.

        Args:
            floor: 
                The timed checks that measure the Pauli product the first 
                time around.
            lid: 
                The timed checks that measure the Pauli product the second
                time around.
            end: 
                The first round (modulo schedule length) by which ALL of the
                checks in the drum will have been measured.
            anchor: 
                Coordinates at which to 'anchor' this drum. If None, defaults 
                to the midpoint of the anchors of all checks involved.
        """
        self._assert_lid_valid(lid)
        self._assert_floor_valid(floor)

        super().__init__(floor + lid, end, anchor)
        self.floor = floor
        self.lid = lid

        self.floor_product = self.timed_checks_product(self.floor)
        self.lid_product = self.timed_checks_product(self.lid)
        if not self.floor_product.equal_up_to_sign(self.lid_product):
            raise ValueError(
                f"Can't create a Drum where the floor and lid don't compare "
                f"the same two Pauli products at different timesteps (up to "
                f"sign). Perhaps you meant to use the Detector class or one "
                f"of its other subclasses? Floor has product "
                f"{self.floor_product}, while lid has product "
                f"{self.lid_product}.")

        first_lid_rounds_ago = min([
            rounds_ago for rounds_ago, check in self.lid])
        last_floor_rounds_ago = max([
            rounds_ago for rounds_ago, check in self.floor])
        first_floor_rounds_ago = min([
            rounds_ago for rounds_ago, check in self.floor])
        self.lid_end = self.end
        self.lid_start = end + first_lid_rounds_ago
        self.floor_end = end + last_floor_rounds_ago
        self.floor_start = end + first_floor_rounds_ago

        # Override the base class' repr_keys.
        self.repr_keys = [
            'floor_product.word', 'lid_product.word', 'end', 'floor', 'lid']

    def has_open_lid(
            self, round: int, schedule_length: int
    ) -> Tuple[bool, List[TimedCheck]]:
        """Checks if checks that make up a drum have been performed.

        A drum has an open lid if its floor has been fully measured but its
        lid has not. This method returns whether this drum has an open lid at
        the point immediately AFTER the given round.
            If the lid is open, we also return the checks that have been
        measured so far in this drum.

        Args:
            round:
                the round just measured. Note this should be absolute rather
                than relative (i.e. not modulo the schedule length)
            schedule_length:
                The length of the code's schedule.

        Returns:
            open_lid:
                Whether this drum has an open lid after the given round
            timed_checks:
                If open_lid is True, then this is all the checks in the drum
                that will have been measured at the end of the given round.
                If open_lid is False, this is None.
        """
        relative_round = round % schedule_length
        # A drum might straddle two layers of the code schedule.
        # Therefore two 'halves' of it might appear in a given layer.
        # The only 'copy' of the drum in a given layer that can possibly have
        # an open lid is the one where the lid ends strictly after the given
        # relative round. So first find this.
        lid_end = self.lid_end
        floor_end = self.floor_end
        floor_start = self.floor_start
        if lid_end <= relative_round:
            # Need the later 'copy' of this drum in this layer.
            lid_end += schedule_length
            floor_end += schedule_length
            floor_start += schedule_length

        layer = round // schedule_length
        floor_measured = layer * schedule_length + floor_start >= 0
        open_lid = floor_measured and floor_end <= relative_round < lid_end
        if open_lid:
            # Figure out which checks will have already been measured at this
            # point (immediately after the given round)
            timed_checks = [
                (t, check) for t, check in self.timed_checks
                if t + lid_end <= relative_round]
        else:
            timed_checks = None
        return open_lid, timed_checks

    def checks_at_or_before(
            self, round: int):
        """
        Returns the checks in the drum that would be measured either at or
        before the given round.

        Args:
            round:
                The round that has just happened. Should not be relative.

        """
        checks = [(t, check) for t, check in self.timed_checks if
                  t + round >= 0]
        return checks


    @staticmethod
    def _assert_lid_valid(lid: List[TimedCheck]):
        if len(lid) == 0:
            raise ValueError("Drum lid must contain at least one check!")
        if not any([t == 0 for t, check in lid]):
            raise ValueError(
                "At least one check in a Drum's lid must have time "
                "component 0 - i.e. it must be measured in the detector's "
                "`end` round. (Otherwise the round specified as the `end` "
                f"is not really the end!). The given lid is: {lid}")

    @staticmethod
    def _assert_floor_valid(floor: List[TimedCheck]):
        if len(floor) == 0:
            raise ValueError("Drum floor must contain at least one check!")

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
        sign) is measured in two different rounds. Comparing these two
        outcomes should thus give a deterministic result.

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
        super().__init__(floor + lid, end, anchor)
        self.floor = floor
        self.lid = lid

        self.floor_product = self.timed_checks_product(self.floor)
        self.lid_product = self.timed_checks_product(self.lid)
        if self.floor_product.word.sign not in [1, -1]:
            sign = self.floor_product.word.sign
            raise ValueError(
                f"Can't create a Drum whose floor has sign {sign}. Sign must "
                f"instead be 1 or -1. Floor has timed checks {self.floor}.")
        if self.lid_product.word.sign not in [1, -1]:
            sign = self.lid_product.word.sign
            raise ValueError(
                f"Can't create a Drum whose lid has sign {sign}. Sign must "
                f"instead be 1 or -1. Lid has timed checks {self.lid}.")
        if not self.floor_product.equal_up_to_sign(self.lid_product):
            raise ValueError(
                f"Can't create a Drum where the floor and lid don't compare "
                f"the same two Pauli products at different timesteps (up to "
                f"complex sign in {{1, -1}}). Perhaps you meant to use the "
                f"Detector class or one of its other subclasses? Floor has "
                f"product {self.floor_product}, while lid has product "
                f"{self.lid_product}.")

        last_floor_rounds_ago = max([
            rounds_ago for rounds_ago, check in self.floor])
        first_lid_rounds_ago = min([
            rounds_ago for rounds_ago, check in self.lid])
        self.floor_start = self.start
        self.floor_end = end + last_floor_rounds_ago
        self.lid_start = end + first_lid_rounds_ago
        self.lid_end = self.end

        # Override the base class' repr_keys.
        self.repr_keys = ['floor_product.word', 'lid_product.word', 'floor', 'lid']

    def has_open_lid(
            self, round: int, layer: int, schedule_length: int
    ) -> Tuple[bool, List[TimedCheck]]:
        """Checks if checks that make up a drum have been performed.

        A drum has an open lid if its floor has been fully measured but its
        lid has not. A drum (or a portion of the drum) may appear more than
        once in any layer. This method returns whether any copy of this drum
        in the given layer has an open lid at the point immediately AFTER the
        given round.
            If the lid is open, we also return the checks that have been
        measured so far in this drum.

        Args:
            round:
                The round just measured.
            layer:
                The layer of the check schedule to consider.
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
        # Figure out the floor and lid end of the only possible copy of the
        # drum in this layer that could have an open lid.
        shift = layer * schedule_length
        lid_end = self.lid_end + shift
        if lid_end <= round:
            # Need to shift more - we're interested in the copy of the drum
            # in this layer where the lid ends strictly after the given round.
            shift += schedule_length
            lid_end = self.lid_end + shift
        floor_end = self.floor_end + shift

        open_lid = floor_end <= round < lid_end
        if open_lid:
            # Figure out which checks will have already been measured at this
            # point (immediately after the given round)
            timed_checks = [
                (t, check) for t, check in self.timed_checks
                if t + lid_end <= round]
        else:
            timed_checks = None
        return open_lid, timed_checks

    def checks_at_or_after(
            self, round: int, layer: int, schedule_length: int):
        """Finds the closest checks of a drum.

        Find the first copy of this drum in the given layer whose end is at
        or after the given round, and return the checks in the drum that
        would be measured either at or after this given round.

        Args:
            round:
                The round to consider - note this should be absolute rather
                than relative (i.e. not modulo the schedule length)
            layer:
                The layer of the code's schedule to consider
            schedule_length:
                Length of the code's schedule.

        Returns:
            Checks of the drum that will be measured at or after the given
            round.
        """
        shift = layer * schedule_length
        lid_end = self.lid_end + shift
        if lid_end < round:
            shift += schedule_length
            lid_end = self.lid_end + shift

        checks = [
            (t, check) for t, check in self.timed_checks
            if t + lid_end >= round]
        return checks

from __future__ import annotations
from typing import List, Tuple

from main.building_blocks.Check import Check
from main.building_blocks.detectors.Detector import Detector


class Drum(Detector):
    def __init__(
            self, floor: List[Tuple[int, Check]],
            lid: List[Tuple[int, Check]], end: int):
        """If we learn the value of the same stabilizer at two different
        timesteps, and the stabilizer remained stabilized in this interval,
        then we can multiply together the two values to detect whether an
        error occurred in this interval. This is what a Detector represents:
        its floor is the set of checks multiplied together to tell us the
        value of the stabilizer the first time around, then the lid is the
        set of checks multiplied together to tell us the value of the
        stabilizer the second time around.
          The 'end' denotes (modulo the schedule length) the first round by
        which every check in the detector is measured.
        """
        super().__init__(floor, lid, end)

        # Note down when the first and last checks in the floor
        # were measured.
        first_floor_rounds_ago = min([
            rounds_ago for rounds_ago, check in self.floor])
        self.floor_start = end + first_floor_rounds_ago
        last_floor_rounds_ago = max([
            rounds_ago for rounds_ago, check in self.floor])
        self.floor_end = end + last_floor_rounds_ago

        self.floor_product = self.face_product(self.floor)
        assert self.floor_product.word.sign in [1, -1]
        assert self.floor_product.equal_up_to_sign(self.lid_product)
        self.negate = \
            self.floor_product.word.sign != self.lid_product.word.sign

        self.repr_keys.extend(['floor_product.word', 'floor'])

    def has_open_lid(self, round: int, layer: int, schedule_length: int):
        # TODO - this method is used to finish logical computations fault
        #  tolerantly, by reconstructing stabilizers from destructive final
        #  measurements. Currently only lets one build the whole lid from
        #  these measurements. But we should also allow these measurements
        #  to be used only as the final layer of a lid.
        # A detector has an open lid if its floor has been fully measured but
        # its lid has not. This returns whether this detector, placed in the
        # given layer, has an open lid at the point immediately AFTER the
        # given round.
        shift = layer * schedule_length
        lid_end = self.lid_end + shift
        if lid_end <= round:
            shift += schedule_length

        lid_end = self.lid_end + shift
        floor_end = self.floor_end + shift
        return floor_end <= round < lid_end

    def has_open_floor(self, round: int, layer: int, schedule_length: int):
        # A detector placed in the given layer has an open floor if its entire
        # lid lies on or above this round, but not all of its floor does.
        shift = layer * schedule_length
        lid_end = self.lid_end + shift
        if lid_end < round:
            shift += schedule_length

        floor_start = self.floor_start + shift
        lid_start = self.lid_start + shift
        return floor_start < round <= lid_start

from __future__ import annotations
from typing import List, Tuple

from main.building_blocks.Check import Check
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.building_blocks.pauli.utils import compose
from main.utils.NiceRepr import NiceRepr
from main.utils.utils import modulo_duplicates


class Detector(NiceRepr):
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
        self.floor = floor
        self.lid = lid
        self.final_slice = [check for t, check in self.lid if t == 0]

        # Note down when the first and last checks in the lid were measured
        first_lid_rounds_ago = min(
            rounds_ago for rounds_ago, check in self.lid)
        self.lid_start = end + first_lid_rounds_ago
        self.lid_end = end

        # Similarly, note down when the first and last checks in the floor
        # were measured.
        self.floor_start, self.floor_end = self.floor_window(end)
        self.stabilizer = self.get_stabilizer()

        # # Including the same check twice in a detector does nothing - note
        # # down the checks modulo pairs of duplicates.
        self.checks = modulo_duplicates(self.lid + self.floor, 2)

        # TODO - make DebugFriendly class accept dot notation,
        #  e.g. should allow stabilizer.word to be passed in.
        super().__init__(['stabilizer.word', 'floor', 'lid'])

    def get_stabilizer(self):
        floor_product = self.face_product(self.floor)
        lid_product = self.face_product(self.lid)
        # TODO - Allow sign difference? e.g. can we measure XXXX and -XXXX
        #  and still build a detector from this? What about iXXXX?
        assert floor_product == lid_product
        return lid_product

    def floor_window(self, end):
        first_floor_rounds_ago = min([
            rounds_ago for rounds_ago, check in self.floor])
        floor_start = end + first_floor_rounds_ago
        last_floor_rounds_ago = max([
            rounds_ago for rounds_ago, check in self.floor])
        floor_end = end + last_floor_rounds_ago
        return floor_start, floor_end

    def has_open_top(self, relative_round: int):
        # TODO - not convinced this isn't buggy.
        # TODO - this method is for use in 'finishing off' detectors with
        #  final data qubit measurements. But currently only lets you
        #  build the whole lid from these measurements. Better would be to
        #  let you also build 'the remainder' - e.g. in the honeycomb code there
        #  are detectors whose floor and lid are both XX and ZZ checks, giving
        #  a -YYYYYY stabilizer. Would be good to allow this to be finished
        #  off after measuring just the XX checks of the lid - (if final data
        #  qubit measurements are all in Z basis).
        # A detector has an open top if its floor has been fully measured but
        # its lid has not. This returns whether the detector is open at the
        # point immediately AFTER the given relative round.
        return self.floor_end <= relative_round < self.lid_end

    def has_open_bottom(self, round: int, shift: int):
        # Let 'round' be the round of checks just measured. A detector has an
        # open bottom if its entire lid lies on or above this round, but not
        # all of its floor does. 'shift' is the number of rounds already
        # measured - since lid_start, floor_start etc are modulo the schedule
        # length, this lets us use absolute values for 'round'.
        return self.floor_start + shift < round <= self.lid_start + shift

    def face_product(self, face: List[Tuple[int, Check]]):
        # Pauli multiplication is not commutative so order matters.
        face = sorted(face, key=lambda check: -check[0])
        checks = [check for (_, check) in face]
        paulis = [pauli for check in checks for pauli in check.paulis]
        stabilizer = PauliProduct(compose(paulis))
        return stabilizer

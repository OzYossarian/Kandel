from typing import Tuple, List

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Coordinates
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.utils.NiceRepr import NiceRepr
from main.utils.utils import modulo_duplicates, mid


class Detector(NiceRepr):
    def __init__(
            self, floor: List[Tuple[int, Check]],
            lid: List[Tuple[int, Check]], end: int,
            anchor: Coordinates = None):
        self.floor = floor
        self.lid = lid
        self.final_slice = [check for t, check in self.lid if t == 0]
        # Set negate to True if this compares two Pauli products that differ
        # by a -1. Let subclasses set this themselves. TODO - Remove this!
        self.negate = None

        if anchor is None:
            anchor = mid([check.anchor for _, check in self.lid])
        self.anchor = anchor

        # Including the same check twice in a detector does nothing - note
        # down the checks modulo pairs of duplicates.
        self.checks = modulo_duplicates(self.lid + self.floor, 2)

        # Note down when the first and last checks in the lid were measured
        first_lid_rounds_ago = min(
            rounds_ago for rounds_ago, check in self.lid)
        self.lid_start = end + first_lid_rounds_ago
        self.lid_end = end

        self.lid_product = self.face_product(self.lid)
        assert self.lid_product.word.sign in [1, -1]

        super().__init__(['lid_product.word', 'lid'])

    def face_product(self, face: List[Tuple[int, Check]]):
        # Pauli multiplication is not commutative so order matters.
        face = sorted(face, key=lambda check: -check[0])
        paulis = [
            pauli for (_, check) in face
            for pauli in check.paulis]
        stabilizer = PauliProduct(paulis)
        return stabilizer

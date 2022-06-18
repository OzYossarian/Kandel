from typing import List, Tuple

from main.building_blocks.Check import Check
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.utils.DebugFriendly import DebugFriendly
from main.utils.utils import pauli_composition


class Detector(DebugFriendly):
    def __init__(
            self, floor: List[Tuple[int, Check]],
            lid: List[Tuple[int, Check]]):
        """If we learn the value of the same stabilizer at two different
        timesteps, and the stabilizer remained stabilized in this interval,
        then we can multiply together the two values to detect whether an
        error occurred in this interval. This is what a Detector represents:
        its floor is the set of checks multiplied together to tell us the
        value of the stabilizer the first time around, then the lid is the
        set of checks multiplied together to tell us the value of the
        stabilizer the second time around.
        """
        self.floor = floor
        self.lid = lid

        # TODO - I thought I needed to know the stabilizers that a detector
        #  measure in order to end a tic-tac-toe code simulation. But I don't
        #  think I do anymore, so this method can perhaps be deleted later.
        #  Does provide an assertion that the floor and lid are the same
        #  stabilizer though.
        def get_stabilizer(face: List[Tuple[int, Check]]):
            # Pauli multiplication is not commutative so order matters.
            face = sorted(face, key=lambda check: -check[0])
            checks = [check for (_, check) in face]
            paulis = [pauli for check in checks for pauli in check.paulis]
            composed = pauli_composition(paulis)
            # Sort these paulis into qubit order so that comparison between
            # lid and floor in a minute is valid.
            composed = sorted(composed, key=lambda pauli: pauli.qubit.coords)
            product = PauliProduct(composed)
            return product

        self.floor_stabilizer = get_stabilizer(self.floor)
        self.lid_stabilizer = get_stabilizer(self.lid)
        # Allow sign difference - e.g. can measure XXXX and -XXXX and still
        # build a detector from this.
        assert self.floor_stabilizer.word.word == self.lid_stabilizer.word.word

        super().__init__(['floor', 'lid'])







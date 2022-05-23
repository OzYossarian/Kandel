from typing import List

from main.building_blocks.Check import Check
from main.building_blocks.Pauli import Pauli
from main.building_blocks.PauliLetter import PauliX, PauliZ
from main.compiling.syndrome_extraction.cnot_order.CNOTOrderer import CNOTOrderer


class RotatedSurfaceCodeOrderer(CNOTOrderer):
    def __init__(self):
        super().__init__()
        self.orders = {
            (PauliX, (1, 0)): 0,
            (PauliX, (0, 1)): 1,
            (PauliX, (0, -1)): 2,
            (PauliX, (-1, 0)): 3,
            (PauliZ, (1, 0)): 0,
            (PauliZ, (0, 1)): 2,
            (PauliZ, (0, -1)): 1,
            (PauliZ, (-1, 0)): 3}

    def order(self, check: Check) -> List[Pauli | None]:
        relative_paulis = []
        ordered = [None, None, None, None]
        for pauli in check.paulis:
            relative_coords = (
                pauli.qubit.coords[0] - check.anchor[0],
                pauli.qubit.coords[1] - check.anchor[1])
            relative_paulis.append((pauli, relative_coords))
        for pauli, relative_coords in relative_paulis:
            order = self.orders[(pauli.letter, relative_coords)]
            ordered[order] = pauli
        return ordered



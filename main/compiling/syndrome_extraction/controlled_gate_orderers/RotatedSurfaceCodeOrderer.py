from typing import List

from main.building_blocks.Check import Check
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliX, PauliZ
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import (
    ControlledGateOrderer,
)


class RotatedSurfaceCodeOrderer(ControlledGateOrderer):
    def __init__(self):
        super().__init__()
        self.gate_order = {
            (PauliX, (1, 0)): 0,
            (PauliX, (0, 1)): 1,
            (PauliX, (0, -1)): 2,
            (PauliX, (-1, 0)): 3,
            (PauliZ, (1, 0)): 0,
            (PauliZ, (0, 1)): 2,
            (PauliZ, (0, -1)): 1,
            (PauliZ, (-1, 0)): 3,
        }

    def order(self, check: Check) -> List[Pauli | None]:
        ordered = [None, None, None, None]
        for relative_coords, pauli in check.paulis.items():
            order = self.gate_order[(pauli.letter, relative_coords)]
            ordered[order] = pauli
        return ordered

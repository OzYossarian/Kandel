from typing import List

from main.building_blocks.Check import Check
from main.building_blocks.pauli import Pauli
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import ControlledGateOrderer


class ToricXyzSquaredOrderer(ControlledGateOrderer):
    def __init__(self):
        super().__init__()
        self.xx_order = {
            (2, 0): 1,
            (-2, 0): 4}
        self.xyzxyz_order = {
            (4, 0): 1,
            (2, 2): 3,
            (-2, 2): 5,
            (-4, 0): 4,
            (-2, -2): 2,
            (2, -2): 0}

    def order(self, check: Check) -> List[Pauli | None]:
        paulis: List[Pauli | None] = [None for _ in range(6)]
        ordering = self.xx_order if check.weight == 2 else self.xyzxyz_order
        for offset, pauli in check.paulis.items():
            order = ordering[offset]
            paulis[order] = pauli
        return paulis
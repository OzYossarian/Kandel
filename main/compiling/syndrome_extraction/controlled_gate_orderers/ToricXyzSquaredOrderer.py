from typing import List

from main.building_blocks.Check import Check
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliX, PauliY, PauliZ
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import ControlledGateOrderer


class ToricXyzSquaredOrderer(ControlledGateOrderer):
    def __init__(self):
        super().__init__()
        self.ordering = {
            # XX ordering
            (PauliX, (2, 0)): 1,
            (PauliX, (-2, 0)): 4,
            # XYZXYZ ordering
            (PauliX, (4, 0)): 1,
            (PauliY, (2, 2)): 3,
            (PauliZ, (-2, 2)): 5,
            (PauliX, (-4, 0)): 4,
            (PauliY, (-2, -2)): 2,
            (PauliZ, (2, -2)): 0}
        self.order_length = 6

    def order(self, check: Check) -> List[Pauli | None]:
        expected_weights = [2, 6]
        if check.weight not in expected_weights:
            self.unexpected_weight_error(check, expected_weights)

        return self._order(check, self.order_length, self.ordering)

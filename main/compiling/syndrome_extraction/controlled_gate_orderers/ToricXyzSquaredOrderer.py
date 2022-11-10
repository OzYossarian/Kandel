from typing import List

from main.building_blocks.Check import Check
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import ControlledGateOrderer


class ToricXyzSquaredOrderer(ControlledGateOrderer):
    def __init__(self):
        super().__init__()
        self.ordering = {
            # XX ordering
            (PauliLetter('X'), (2, 0)): 1,
            (PauliLetter('X'), (-2, 0)): 4,
            # XYZXYZ ordering
            (PauliLetter('X'), (4, 0)): 1,
            (PauliLetter('Y'), (2, 2)): 3,
            (PauliLetter('Z'), (-2, 2)): 5,
            (PauliLetter('X'), (-4, 0)): 4,
            (PauliLetter('Y'), (-2, -2)): 2,
            (PauliLetter('Z'), (2, -2)): 0}
        self.order_length = 6

    def order(self, check: Check) -> List[Pauli | None]:
        expected_weights = [2, 6]
        if check.weight not in expected_weights:
            self.unexpected_weight_error(check, expected_weights)

        return self._order(check, self.order_length, self.ordering)

    def __eq__(self, other):
        # Any two instances of a ToricXyzSquaredOrderer are equal!
        return type(self) == type(other)

    def __hash__(self):
        return hash(type(self))

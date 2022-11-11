from typing import List, Union

from main.building_blocks.Check import Check
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import (
    ControlledGateOrderer,
)


class RotatedSurfaceCodeOrderer(ControlledGateOrderer):
    """
    A controlled gate orderer specifically for the rotated surface code.
    This defines the timesteps within a syndrome extraction round at which
    different data qubits should have a controlled gate between themself
    and the ancilla qubit.
    """
    def __init__(self):
        super().__init__()
        self.ordering = {
            (PauliLetter('X'), (1, 0)): 0,
            (PauliLetter('X'), (0, 1)): 2,
            (PauliLetter('X'), (0, -1)): 1,
            (PauliLetter('X'), (-1, 0)): 3,
            (PauliLetter('Z'), (1, 0)): 0,
            (PauliLetter('Z'), (0, 1)): 1,
            (PauliLetter('Z'), (0, -1)): 2,
            (PauliLetter('Z'), (-1, 0)): 3}
        self.order_length = 4

    def order(self, check: Check) -> List[Union[Pauli,None]]:
        expected_weights = [2, 4]
        if check.weight not in expected_weights:
            self.unexpected_weight_error(check, expected_weights)
        expected_words = ['XXXX', 'ZZZZ', 'XX', 'ZZ']
        if check.product.word.word not in expected_words:
            self.unexpected_word_error(check, expected_words)

        return self._order(check, self.order_length, self.ordering)

    def __eq__(self, other):
        # Any two instances of a RotatedSurfaceCodeOrderer are equal!
        return type(self) == type(other)

    def __hash__(self):
        return hash(type(self))

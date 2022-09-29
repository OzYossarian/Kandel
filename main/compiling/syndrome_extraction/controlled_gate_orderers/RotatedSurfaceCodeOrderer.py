from typing import List

from main.building_blocks.Check import Check
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliX, PauliZ
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
            (PauliX, (1, 0)): 0,
            (PauliX, (0, 1)): 2,
            (PauliX, (0, -1)): 1,
            (PauliX, (-1, 0)): 3,
            (PauliZ, (1, 0)): 0,
            (PauliZ, (0, 1)): 1,
            (PauliZ, (0, -1)): 2,
            (PauliZ, (-1, 0)): 3}
        self.order_length = 4

    def order(self, check: Check) -> List[Pauli | None]:
        expected_weights = [2, 4]
        if check.weight not in expected_weights:
            self.unexpected_weight_error(check, expected_weights)
        expected_words = ['XXXX', 'ZZZZ', 'XX', 'ZZ']
        if check.product.word.word not in expected_words:
            self.unexpected_word_error(check, expected_words)

        return self._order(check, self.order_length, self.ordering)
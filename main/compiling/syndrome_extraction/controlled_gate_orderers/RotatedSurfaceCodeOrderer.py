from typing import List

from main.building_blocks.Check import Check
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliX, PauliZ
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import (
    ControlledGateOrderer,
)
from main.utils.types import Coordinates


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

    def order(self, check: Check) -> List[Pauli | None]:
        if check.weight not in [2, 4]:
            self.unexpected_weight_error(check)
        if check.product.word.word not in ['XXXX', 'ZZZZ', 'XX', 'ZZ']:
            self.unexpected_word_error(check)
        ordered = [None, None, None, None]
        for offset, pauli in check.paulis.items():
            key = (pauli.letter, offset)
            if key in self.ordering:
                order = self.ordering[key]
                ordered[order] = pauli
            else:
                self.unexpected_pauli_error(check, pauli, offset)
        return ordered

    def unexpected_pauli_error(
            self, check: Check, pauli: Pauli, offset: Coordinates):
        raise ValueError(
            f"Check contains an unexpected Pauli! "
            f"Found a Pauli {pauli} with coords {offset} "
            f"relative to check anchor {check.anchor}. "
            f"Expected only the following Pauli letters and relative "
            f"coordinates: {self.ordering}")

    def unexpected_weight_error(self, check: Check):
        raise ValueError(
            f"Check has unexpected weight! "
            f"Expected check to have weight 2 or 4, "
            f"but instead it has weight {check.weight}. "
            f"Check is: {check}.")

    def unexpected_word_error(self, check: Check):
        raise ValueError(
            f"Check has unexpected word! "
            f"Expected check to have word XXXX, ZZZZ, XX or ZZ, "
            f"but instead it has word {check.product.word.word}. "
            f"Check is: {check}.")

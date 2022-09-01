from typing import List

from main.building_blocks.Check import Check
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliX, PauliY, PauliZ
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import ControlledGateOrderer
from main.utils.types import Coordinates


class ToricXyzSquaredOrderer(ControlledGateOrderer):
    def __init__(self):
        super().__init__()
        self.xx_ordering = {
            (PauliX, (2, 0)): 1,
            (PauliX, (-2, 0)): 4}
        self.xyzxyz_ordering = {
            (PauliX, (4, 0)): 1,
            (PauliY, (2, 2)): 3,
            (PauliZ, (-2, 2)): 5,
            (PauliX, (-4, 0)): 4,
            (PauliY, (-2, -2)): 2,
            (PauliZ, (2, -2)): 0}

    def order(self, check: Check) -> List[Pauli | None]:
        if check.weight not in [2, 6]:
            self.unexpected_weight_error(check)
        ordering = self.xx_ordering \
            if check.weight == 2 \
            else self.xyzxyz_ordering

        ordered: List[Pauli | None] = [None for _ in range(6)]
        for offset, pauli in check.paulis.items():
            key = (pauli.letter, offset)
            if key in ordering:
                order = ordering[key]
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
            f"coordinates: {self.xx_ordering} or {self.xyzxyz_ordering}")

    def unexpected_weight_error(self, check: Check):
        raise ValueError(
            f"Check has unexpected weight! "
            f"Expected check to have weight 2 or 6, "
            f"but instead it has weight {check.weight}. "
            f"Check is: {check}.")

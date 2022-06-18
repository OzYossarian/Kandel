from typing import List

from main.building_blocks.pauli.Pauli import Pauli
from main.utils.utils import pauli_composition


class LogicalOperator:
    def __init__(self, paulis: List[Pauli]):
        self.paulis = paulis

    def update(self, other_paulis: List[Pauli]):
        # Compose the logical operator with these new paulis, to give
        # a new logical operator.
        self.paulis = pauli_composition(other_paulis + self.paulis)

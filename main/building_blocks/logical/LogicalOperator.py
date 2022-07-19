from typing import List

from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.utils import compose


class LogicalOperator:
    def __init__(self, paulis: List[Pauli]):
        # the logical operator may move around, so we save both initial paulis
        # and a mutable copy
        self.initial_paulis = paulis
        self.paulis = paulis.copy()

    def update(self, other_paulis: List[Pauli]):
        # Compose the logical operator with these new paulis, to give
        # a new logical operator.
        self.paulis = compose(other_paulis + self.paulis)

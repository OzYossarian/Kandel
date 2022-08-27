from typing import List

from main.building_blocks.Check import Check
from main.building_blocks.pauli.Pauli import Pauli


class LogicalOperator:
    def __init__(self, paulis: List[Pauli]):
        """
        Class representing a logical operator. This base class assumes it's
        'static' (defined by the same Paulis at all times). A 'dynamic'
        logical operator (one defined by different Paulis at different times)
        should subclass this.

        Args:
            paulis: the Paulis that constitute the operator.
        """
        # Shouldn't access _paulis directly; instead, use at_round.
        self._paulis = paulis
        super().__init__()

    def update(self, round: int) -> List[Check]:
        """
        Updates the list of Paulis that form the logical operator at this
        round. This base class assumes a static logical operator, as in a
        stabilizer or subsystem code. A dynamic logical operator should
        override this class with its own rules as to how the operator
        changes at each round.

        Args:
            round: the round that has just happened

        Returns:
            a list of any checks that need multiplying into the observable
        """
        return []

    def at_round(self, round: int):
        """
        Args:
            round: the round that has just happened

        Returns:
            the Paulis that constitute the logical operator at this round
        """
        return self._paulis


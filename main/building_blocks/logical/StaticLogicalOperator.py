class StaticLogicalOperator(LogicalOperator):
    def __init__(self, paulis: List[Pauli]):
        """
        Class representing a static logical operator 
        (defined by the same Paulis at all times).

        Args:
            paulis: the Paulis that constitute the operator.
        """
        super().__init__(paulis)


    def update(self, round: int) -> List[Check]:
        """
        Static logical operators by definition don't change over time.
        So this method always returns an empty list.

        Args:
            round: the round that has just happened

        Returns:
            an empty list
        """
        return []

    def at_round(self, round: int) -> List[Pauli]:
        """
        Args:
            round: the round that has just happened

        Returns:
            the Paulis that constitute the logical operator at this round
        """
        return self._paulis
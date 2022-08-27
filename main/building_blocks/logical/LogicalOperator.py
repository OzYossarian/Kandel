from typing import List

from main.building_blocks.Check import Check
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliProduct import PauliProduct


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
        self._assert_qubits_unique(paulis)
        self._assert_coords_valid(paulis)

        product = PauliProduct(paulis)
        self._assert_is_hermitian(product, paulis)

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

    @staticmethod
    def _assert_qubits_unique(paulis: List[Pauli]):
        qubits = [pauli.qubit for pauli in paulis]
        if len(set(qubits)) != len(qubits):
            raise ValueError(
                f"Can't include the same qubit more than once in a logical "
                f"operator! Paulis that make up the operator are: {paulis}")

    @staticmethod
    def _assert_coords_valid(paulis: List[Pauli]):
        dimensions = {pauli.dimension for pauli in paulis}
        if len(dimensions) > 1:
            raise ValueError(
                f"Paulis within a logical operator must all have the same "
                f"dimension. Instead, found dimensions {dimensions}. "
                f"Paulis that make up the operator are: {paulis}")
        all_tuples = all([
            isinstance(pauli.qubit.coords, tuple) for pauli in paulis])
        all_non_tuples = not any([
            isinstance(pauli.qubit.coords, tuple) for pauli in paulis])
        if not (all_tuples or all_non_tuples):
            raise ValueError(
                f"Can't mix tuple and non-tuple coordinates! "
                f"Paulis that make up the operator are: {paulis}")

    @staticmethod
    def _assert_is_hermitian(
            product: PauliProduct, paulis: List[Pauli]):
        if not product.is_hermitian:
            raise ValueError(
                f"The product of all Paulis in a logical operator must be "
                f"Hermitian! Given Paulis are {paulis}.")

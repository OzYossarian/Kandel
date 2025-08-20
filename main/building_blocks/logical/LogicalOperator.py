from abc import abstractmethod
from typing import List

from main.building_blocks.Check import Check
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.utils.NiceRepr import NiceRepr


class LogicalOperator(NiceRepr):
    def __init__(self, paulis: List[Pauli]):
        # Shouldn't access _paulis directly; instead, use at_round.
        self._paulis = paulis
        self._assert_non_empty()
        self._assert_qubits_unique()
        self._assert_coords_valid()
        super().__init__(['_paulis'])

    @property
    def dimension(self):
        return self.at_round(-1)[0].dimension

    @property
    def has_tuple_coords(self):
        return self.at_round(-1)[0].has_tuple_coords

    @abstractmethod
    def update(self, round: int) -> List[Check]:
        """
        Update the logical operator after the given round.
        For static logical operators, this does nothing.
        Dynamic logical operators might require checks to be multiplied in.

        Args:
            round: the round that has just happened

        Returns:
            the checks to be multiplies into the logical operator at this round
        """
        pass

    @abstractmethod
    def at_round(self, round: int) -> List[Pauli]:
        """
        Get a list of Paulis that constitute the logical operator at the given round.
        For static logical operators, this returns the same list at all rounds.
        For dynamic logical operators, this may change from round to round.

        Args:
            round: the round that has just happened

        Returns:
            the Paulis that constitute the logical operator at this round
        """
        pass

    def _assert_non_empty(self):
        paulis = self.at_round(-1)
        if len(paulis) == 0:
            raise ValueError(
                "Can't create a logical operator from an empty list of "
                "Paulis.")

    def _assert_qubits_unique(self):
        paulis = self.at_round(-1)
        qubits = [pauli.qubit for pauli in paulis]
        if len(set(qubits)) != len(qubits):
            raise ValueError(
                f"Can't include the same qubit more than once in a logical "
                f"operator! Paulis that make up the operator are: {paulis}")

    def _assert_coords_valid(self):
        paulis = self.at_round(-1)
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

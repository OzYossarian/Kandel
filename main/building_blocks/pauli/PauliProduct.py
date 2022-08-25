from __future__ import annotations

from typing import Collection, List

from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliWord import PauliWord
from main.building_blocks.pauli.utils import compose
from main.utils.NiceRepr import NiceRepr


class PauliProduct(NiceRepr):
    def __init__(self, paulis: List[Pauli], identities_removed: bool = False):
        """Class representing a tensor product of Paulis.

        Args:
            paulis: the Paulis to be tensored together. It's possible to pass in
                multiple Paulis acting on the same qubit, but note that all
                Paulis acting on the same qubit will be composed to give a
                single Pauli. Since Paulis don't necessarily commute, order
                matters.

            identities_removed: if all the paulis with letter I have signs that multiply to 1,
                and this flag is set to True, then all such paulis will be
                removed. Note that this is applied after any composition of
                Paulis. e.g. if `paulis` contains two Xs on the same qubit,
                these will be composed to an I, and then are eligible for
                removal.
        """
        self._assert_paulis_valid(paulis)

        unique_qubits = {pauli.qubit for pauli in paulis}
        if len(unique_qubits) != len(paulis):
            # At least one qubit has multiple Paulis acting on it. So let's
            # compose all the Paulis on these qubits, so that we have exactly
            # one Pauli on each qubit.
            paulis = compose(paulis, identities_removed)
        self.paulis = paulis
        self.weight = len(paulis)
        letters = [pauli.letter for pauli in self.paulis]
        self.word = PauliWord.from_letters(letters)

        self._is_identity = None
        self._is_hermitian = None

        # Define the following internal properties for use in comparisons.
        sorted_paulis = sorted(
            self.paulis, key=lambda pauli: pauli.qubit.coords)
        self._sorted_qubits = tuple(pauli.qubit for pauli in sorted_paulis)
        sorted_letters = [pauli.letter for pauli in sorted_paulis]
        self._sorted_word = PauliWord.from_letters(sorted_letters)

        repr_keys = ['word', 'paulis']
        super().__init__(repr_keys)

    @property
    def is_identity(self):
        if self._is_identity is None:
            self._is_identity = \
                self.word.sign == 1 and \
                all(letter == "I" for letter in self.word.word)
        return self._is_identity

    @property
    def is_hermitian(self):
        if self._is_hermitian is None:
            # It's Hermitian iff it's self-adjoint. And since it's unitary, this is
            # equivalent to saying it's self-inverse.
            product_with_itself = PauliProduct(self.paulis + self.paulis)
            self._is_hermitian = product_with_itself.is_identity
        return self._is_hermitian

    @staticmethod
    def _assert_paulis_valid(paulis: Collection[Pauli]):
        dimensions = {pauli.dimension for pauli in paulis}
        if len(dimensions) > 1:
            raise ValueError(
                f"Paulis within a check must all have the same dimension. "
                f"Instead, found dimensions {dimensions}. "
                f"The given Paulis are: {list(paulis)}")
        all_tuples = all([pauli.has_tuple_coords for pauli in paulis])
        all_non_tuples = all([not pauli.has_tuple_coords for pauli in paulis])
        if not (all_tuples or all_non_tuples):
            raise ValueError(
                f"Can't mix tuple and non-tuple coordinates! "
                f"The given Paulis are: {list(paulis)}")

    # TODO - do we actually want to allow this? Answer: YES!
    def equal_up_to_sign(self, other: PauliProduct):
        return \
            self._sorted_qubits == other._sorted_qubits and \
            self._sorted_word.word == other._sorted_word.word

    def __eq__(self, other):
        return \
            type(other) == type(self) and \
            self._sorted_qubits == other._sorted_qubits and \
            self._sorted_word == other._sorted_word

    def __hash__(self):
        return hash((self._sorted_qubits, self._sorted_word))

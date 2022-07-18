from __future__ import annotations

from typing import Iterable

from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliWord import PauliWord
from main.building_blocks.pauli.utils import compose
from main.utils.NiceRepr import NiceRepr


class PauliProduct(NiceRepr):
    def __init__(self, paulis: Iterable[Pauli], composed: bool = False):
        """ Class representing a tensor product of Paulis.
        """
        if not composed:
            self.paulis = compose(paulis)
        letters = [pauli.letter for pauli in self.paulis]
        self.word = PauliWord.from_letters(letters)

        # Define the following extra properties for use in comparisons.
        sorted_paulis = sorted(
            self.paulis, key=lambda pauli: pauli.qubit.coords)
        self.qubits = tuple(pauli.qubit for pauli in sorted_paulis)
        sorted_letters = [pauli.letter for pauli in sorted_paulis]
        self.sorted_word = PauliWord.from_letters(sorted_letters)

        repr_keys = ['word', 'paulis']
        super().__init__(repr_keys)

    # TODO - do we actually want to allow this?
    def equal_up_to_sign(self, other: PauliProduct):
        return \
            self.qubits == other.qubits and \
            self.sorted_word.word == other.sorted_word.word

    def __eq__(self, other):
        return \
            type(other) == type(self) and \
            self.qubits == other.qubits and \
            self.sorted_word == other.sorted_word

    def __hash__(self):
        return hash((self.qubits, self.sorted_word))



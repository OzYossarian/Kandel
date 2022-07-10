from typing import List

from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliWord import PauliWord
from main.utils.DebugFriendly import DebugFriendly


class PauliProduct(DebugFriendly):
    def __init__(self, paulis: List[Pauli]):
        """ Class representing a tensor product of Paulis.
        """
        self.paulis = paulis
        letters = [pauli.letter for pauli in paulis]
        self.word = PauliWord.from_letters(letters)

        # Define the following extra properties for use in comparisons.
        sorted_paulis = sorted(paulis, key=lambda pauli: pauli.qubit.coords)
        self.qubits = tuple(set(pauli.qubit for pauli in sorted_paulis))
        sorted_letters = [pauli.letter for pauli in sorted_paulis]
        self.sorted_word = PauliWord.from_letters(sorted_letters)

        repr_keys = ['word', 'paulis']
        super().__init__(repr_keys)

    def __eq__(self, other):
        return \
            type(other) == type(self) and \
            self.qubits == other.qubits and \
            self.sorted_word == other.sorted_word

    def __hash__(self):
        return hash((self.qubits, self.sorted_word))



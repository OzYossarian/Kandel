import operator
from functools import reduce
from typing import List

from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.utils.NiceRepr import NiceRepr


class PauliWord(NiceRepr):
    def __init__(self, word: str, sign: complex = 1):
        """ PauliWord is more abstract than a PauliProduct, in that it doesn't
        need to specify any actual qubits that it applies to. The relationship
        between PauliWords and PauliProducts is the same as the relationship
        between PauliLetters and Paulis.
        """
        if not len(word) > 0:
            raise ValueError(f"Can't create an 'empty' PauliWord.")
        if not all([letter in ['I', 'X', 'Y', 'Z'] for letter in word]):
            raise ValueError(
                f"Only valid Pauli letters are I, X, Y and Z. "
                f"Cannot use {word} as a PauliWord")
        if sign not in [1, 0 + 1j, -1, 0 - 1j]:
            raise ValueError(
                f"Only valid signs are 1, j, -1, -j. "
                f"Cannot use {sign} as a sign for a PauliWord.")
        self.word = word
        self.sign = sign
        super().__init__(['word', 'sign'])

    @classmethod
    def from_letters(cls, letters: List[PauliLetter]):
        word = ''.join([letter.letter for letter in letters])
        signs = [letter.sign for letter in letters]
        sign = reduce(operator.mul, signs, 1)
        return cls(word, sign)

    def __eq__(self, other):
        return \
            type(other) == type(self) and \
            self.word == other.word and \
            self.sign == other.sign

    def __hash__(self):
        return hash((self.word, self.sign))



from functools import reduce
from typing import List

from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.utils.DebugFriendly import DebugFriendly


class PauliWord(DebugFriendly):
    def __init__(self, word: str, sign: complex = 1):
        """ PauliWord is more abstract than a PauliProduct, in that it doesn't
        need to specify any actual qubits that it applies to. The relationship
        between PauliWords and PauliProducts is the same as the relationship
        between PauliLetters and Paulis.
        """
        self.word = word
        self.sign = sign
        super().__init__(['word', 'sign'])

    @classmethod
    def from_letters(cls, letters: List[PauliLetter]):
        word = ''.join([letter.letter for letter in letters])
        signs = [letter.sign for letter in letters]
        sign = reduce(lambda x, y: x*y, signs)
        return cls(word, sign)

    def __eq__(self, other):
        return \
            type(other) == type(self) and \
            self.word == other.word and \
            self.sign == other.sign

    def __hash__(self):
        return hash((self.word, self.sign))



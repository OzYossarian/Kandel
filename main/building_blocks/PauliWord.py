from functools import reduce
from typing import Iterable, List

from main.building_blocks.PauliLetter import PauliLetter
from main.utils.DebugFriendly import DebugFriendly


class PauliWord(DebugFriendly):
    def __init__(self, word: str, sign: complex):
        self.word = word
        self.sign = sign
        super().__init__(['word', 'sign'])

    @classmethod
    def from_letters(cls, letters: List[PauliLetter]):
        word = ''.join([letter.letter for letter in letters])
        signs = [letter.sign for letter in letters]
        sign = reduce(lambda x, y: x*y, signs)
        return cls(word, sign)



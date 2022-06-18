from typing import List

from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliWord import PauliWord


class PauliProduct:
    def __init__(self, paulis: List[Pauli]):
        self.paulis = paulis
        letters = [pauli.letter for pauli in paulis]
        self.word = PauliWord.from_letters(letters)



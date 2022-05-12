from main.building_blocks.PauliLetter import PauliLetter
from main.building_blocks.Qubit import Qubit
from main.utils.DebugFriendly import DebugFriendly


class Pauli(DebugFriendly):
    def __init__(self, qubit: Qubit, letter: PauliLetter):
        self.qubit = qubit
        self.letter = letter
        super().__init__(['qubit', 'letter'])

    def __eq__(self, other):
        return \
            type(self) == type(other) and \
            self.qubit == other.qubit and \
            self.letter == other.letter

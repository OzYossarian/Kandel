from main.building_blocks.pauli.PauliLetter import PauliLetter
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

    def __hash__(self):
        return hash((self.qubit, self.letter))

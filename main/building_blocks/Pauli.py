from main.building_blocks.PauliLetter import PauliLetter
from main.building_blocks.Qubit import Qubit
from main.utils.DebugFriendly import DebugFriendly


class Pauli(DebugFriendly):
    def __init__(self, qubit: Qubit, letter: PauliLetter):
        self.qubit = qubit
        self.letter = letter
        super().__init__(['qubit', 'letter'])

    def __eq__(self, other):
        if isinstance(other, Pauli) \
                and self.qubit == other.qubit \
                and self.letter == other.letter:
            return True
        else:
            return False

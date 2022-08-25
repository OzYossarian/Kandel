from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.Qubit import Qubit
from main.utils.NiceRepr import NiceRepr


class Pauli(NiceRepr):
    def __init__(self, qubit: Qubit, letter: PauliLetter):
        self.qubit = qubit
        self.letter = letter
        self.dimension = qubit.dimension
        super().__init__(['qubit', 'letter'])

    @property
    def has_tuple_coords(self):
        return isinstance(self.qubit.coords, tuple)

    def __eq__(self, other):
        return \
            type(self) == type(other) and \
            self.qubit == other.qubit and \
            self.letter == other.letter

    def __hash__(self):
        return hash((self.qubit, self.letter))

from main.Colour import Colour, Red, Blue, Green
from main.utils import DebugFriendly


class Pauli(DebugFriendly):
    def __init__(self, name: str, colour: Colour):
        self.name = name
        # Paulis come with a default colour to be used e.g. when printing.
        # Not to be confused with the colour of an edge/plaquette/etc. when
        # using e.g. colour code.
        self.colour = colour


PauliX = Pauli('X', Red)
PauliY = Pauli('Y', Blue)
PauliZ = Pauli('Z', Green)

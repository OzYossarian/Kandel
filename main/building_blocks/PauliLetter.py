from main.Colour import Colour, Red, Blue, Green
from main.utils.DebugFriendly import DebugFriendly


class PauliLetter(DebugFriendly):
    def __init__(self, letter: str, colour: Colour):
        self.letter = letter
        # Paulis come with a default colour to be used e.g. when printing.
        # Not to be confused with the colour of an edge/plaquette/etc. when
        # using e.g. colour code.
        self.colour = colour
        super().__init__(['letter'])


PauliX = PauliLetter('X', Red)
PauliY = PauliLetter('Y', Blue)
PauliZ = PauliLetter('Z', Green)

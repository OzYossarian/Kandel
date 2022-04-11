from main.Colour import Colour, Red, Blue, Green


class Pauli:
    def __init__(self, name: str, colour: Colour):
        self.name = name
        # Paulis come with a default colour to be used e.g. when printing.
        # Not to be confused with the colour of an edge/plaquette/etc. when
        # using colour code or similar.
        self.colour = colour


PauliX = Pauli('X', Red)
PauliY = Pauli('Y', Blue)
PauliZ = Pauli('Z', Green)

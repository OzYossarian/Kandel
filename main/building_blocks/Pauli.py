from main.Colour import Colour, Red, Blue, Green


class Pauli:
    def __init__(self, name: str, colour: Colour):
        self.name = name
        self.colour = colour


PauliX = Pauli('X', Red)
PauliY = Pauli('Y', Blue)
PauliZ = Pauli('Z', Green)
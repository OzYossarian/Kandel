from enum import Enum


class State(Enum):
    Zero = 0
    One = 1


class Colour(Enum):
    Red = 0
    Blue = 1
    Green = 2


class Pauli(Enum):
    X = 0
    Y = 1
    Z = 2


class Layout(Enum):
    Hexagonal = 0
    Brickwork = 1


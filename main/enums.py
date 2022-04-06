from enum import Enum


class State(Enum):
    Zero = 0
    One = 1
    Plus = 2
    Minus = 3


class Layout(Enum):
    Hexagonal = 0
    Brickwork = 1

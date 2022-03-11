from typing import Tuple
from main.enums import State


Coordinates = Tuple[int, ...] | int


class Qubit:
    def __init__(self, position: Tuple[int, ...], initial_state: State):
        self.position = position
        self.initial_state = initial_state

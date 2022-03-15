from typing import Tuple
from main.enums import State


Coordinates = Tuple[int, ...] | int


class Qubit:
    def __init__(self, coords: Tuple[int, ...], initial_state: State):
        self.coords = coords
        self.initial_state = initial_state

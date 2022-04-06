from typing import Tuple
from main.enums import State


Coordinates = Tuple[int, ...] | int


class Qubit(object):
    def __init__(self, coords: Coordinates, initial_state: State):
        self.coords = coords
        self.initial_state = initial_state

    def __repr__(self):
        return f"position={self.coords}, state=|{self.initial_state.value}>"

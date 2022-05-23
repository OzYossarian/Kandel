from typing import Tuple
from main.enums import State
from main.utils.DebugFriendly import DebugFriendly

Coordinates = Tuple[int, ...] | int


class Qubit(DebugFriendly):
    def __init__(self, coords: Coordinates, initial_state: State = None):
        self.coords = coords
        self.initial_state = initial_state
        super().__init__(['coords'])

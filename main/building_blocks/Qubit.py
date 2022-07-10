from typing import Tuple
from main.utils.DebugFriendly import DebugFriendly

Coordinates = Tuple[int, ...] | int


class Qubit(DebugFriendly):
    def __init__(self, coords: Coordinates):
        self.coords = coords
        super().__init__(['coords'])

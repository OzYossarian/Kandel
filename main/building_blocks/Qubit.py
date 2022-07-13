from typing import Tuple
from main.utils.NiceRepr import NiceRepr

Coordinates = Tuple[int, ...] | int


class Qubit(NiceRepr):
    def __init__(self, coords: Coordinates):
        self.coords = coords
        super().__init__(['coords'])

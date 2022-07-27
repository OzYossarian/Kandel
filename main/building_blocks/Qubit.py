from typing import Tuple
from main.utils.NiceRepr import NiceRepr

# ToDo - allow complex numbers too? Check there's no arithmetic being
#  done that would prevent this.
Coordinates = Tuple[int | float, ...] | int | float


class Qubit(NiceRepr):
    def __init__(self, coords: Coordinates):
        self.coords = coords
        super().__init__(['coords'])

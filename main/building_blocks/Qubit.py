from typing import Tuple
from main.utils.NiceRepr import NiceRepr
from main.utils.utils import coords_length

Coordinates = Tuple[int | float, ...] | int | float
# ToDo - allow complex numbers too? Check there's no arithmetic being
#  done that would prevent this.


class Qubit(NiceRepr):
    def __init__(self, coords: Coordinates):
        self.coords = coords
        self.dimension = coords_length(coords)
        super().__init__(['coords'])

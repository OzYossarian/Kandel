from typing import Tuple
from main.utils.NiceRepr import NiceRepr
from main.utils.utils import coords_length


Coordinates = Tuple[int | float, ...] | int | float
# TODO - allow complex numbers too! Would need to adapt some methods -
#  e.g. finding mean of coordinates using statistics.mean would break.


class Qubit(NiceRepr):
    def __init__(self, coords: Coordinates):
        self.coords = coords
        self.dimension = coords_length(coords)
        super().__init__(['coords'])

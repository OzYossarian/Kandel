from main.utils.NiceRepr import NiceRepr
from main.utils.types import Coordinates
from main.utils.utils import coords_length


class Qubit(NiceRepr):
    def __init__(self, coords: Coordinates):
        self.coords = coords
        self.dimension = coords_length(coords)
        super().__init__(['coords'])

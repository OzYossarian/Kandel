from main.utils.NiceRepr import NiceRepr
from main.utils.types import Coordinates
from main.utils.utils import coords_length


class Qubit(NiceRepr):
    def __init__(self, coords: Coordinates):
        self.coords = coords
        super().__init__(['coords'])

    @property
    def dimension(self):
        return coords_length(self.coords)

    @property
    def has_tuple_coords(self):
        return isinstance(self.coords, tuple)

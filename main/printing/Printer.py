from main.QPUs.QPU import QPU
from main.utils.types import Coordinates
from main.utils.utils import coords_sum


class Printer:
    def __init__(self, scale_factor: int = 10):
        self.scale_factor = scale_factor

    def scale(self, coords: Coordinates, offset: Coordinates):
        if isinstance(coords, tuple):
            assert isinstance(offset, tuple)
            coords = coords_sum(coords, offset)
            return tuple(map(lambda x: x * self.scale_factor, coords))
        else:
            # So 'coords' and 'offset' must just be integers.
            assert isinstance(offset, int)
            return (coords + offset) * self.scale_factor

    def print_qpu(self, qpu: type(QPU), filename: str):
        pass


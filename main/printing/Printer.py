from main.QPUs.QPU import QPU
from main.building_blocks.Qubit import Coordinates
from main.utils.utils import tuple_sum


class Printer:
    def __init__(self, scale_factor: int = 10):
        self.scale_factor = scale_factor

    def scale(self, coords: Coordinates, offset: Coordinates):
        if isinstance(coords, tuple):
            assert isinstance(offset, tuple)
            coords = tuple_sum(coords, offset)
            return tuple(map(lambda x: x * self.scale_factor, coords))
        else:
            # So 'coords' and 'offset' must just be integers.
            assert isinstance(offset, int)
            return (coords + offset) * self.scale_factor

    def print_qpu(self, qpu: type(QPU), filename: str):
        pass


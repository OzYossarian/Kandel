from typing import Dict, List, Iterable, Tuple

from main.QPUs.QPU import QPU
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Coordinates, Qubit
from main.codes.Code import Code
from main.enums import Layout


class HexagonalCode(Code):
    def __init__(self, data_qubits: Dict[Coordinates, type(Qubit)],
                 schedule: List[Iterable[type(Check)]], layout: Layout):
        self.layout = layout
        super().__init__(data_qubits, schedule)

    def transform_coords(self, qpu: QPU):
        # TODO - for now, only embed into square lattice QPUs.
        assert isinstance(qpu, SquareLatticeQPU)

        if self.layout == Layout.Hexagonal:
            transform = self.hexagonal_square_lattice_coords
        elif self.layout == Layout.Brickwork:
            transform = self.brickwork_square_lattice_coords
        else:
            raise ValueError('Currently only hexagonal and brickwork layouts '
                             'are supported')

        for check in self.checks:
            check.center = transform(check.center)
        for qubit in self.data_qubits.values():
            qubit.coords = transform(qubit.coords)

    @staticmethod
    def get_neighbours(coords: Tuple[int, int, int]):
        # These coordinates must be returned in 'polygonal order' - i.e.
        # such that two coordinates adjacent in this list are adjacent
        # corners when drawing this plaquette as a polygon.
        (g, x, y) = coords
        g_ = (g + 1) % 2
        e = -1 if g == 0 else 1
        return [
            (g, x + e, y),
            (g_, x + e, y),
            (g_, x, y),
            (g, x - e, y),
            (g_, x, y + e),
            (g_, x + e, y + e),
        ]

    @staticmethod
    def hexagonal_square_lattice_coords(coords: Coordinates):
        (g, x, y) = coords
        return (2*x + g, 4*y + 2*g)

    @staticmethod
    def brickwork_square_lattice_coords(coords: Coordinates):
        x_, y_ = HexagonalCode.hexagonal_square_lattice_coords(coords)
        x_ -= (x_ + 2) // 3
        return (x_, y_)
from typing import Dict, List, Tuple

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Coordinates, Qubit
from main.codes.Code import Code


class HexagonalCode(Code):
    def __init__(self, data_qubits: Dict[Coordinates, Qubit],
                 schedule: List[List[Check]]):
        super().__init__(data_qubits, schedule)

    @staticmethod
    def get_neighbours(coords: Tuple[int, int]) -> List[Tuple[int, int]]:
        # These coordinates must be returned in 'polygonal order' - i.e.
        # such that two coordinates adjacent in this list are adjacent
        # corners when drawing this plaquette as a polygon.
        (x, y) = coords
        return [
            (x + 4, y),
            (x + 2, y + 2),
            (x - 2, y + 2),
            (x - 4, y),
            (x - 2, y - 2),
            (x + 2, y - 2),
        ]

    @staticmethod
    def is_plaquette_column(x_coord: int):
        return (x_coord - 4) % 6 == 0

    @staticmethod
    def plaquette_in_shifted_column(plaquette_center_x_coord: int):
        return bool(((plaquette_center_x_coord - 4) // 6) % 2)

    @staticmethod
    def data_qubit_in_shifted_column(data_qubit_x_coord: int):
        return bool(((data_qubit_x_coord - 2) // 6) % 2)

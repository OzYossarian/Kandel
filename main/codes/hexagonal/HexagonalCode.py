from typing import Dict, List, Tuple

from main.Colour import Red, Green, Blue
from main.building_blocks.Check import Check
from main.building_blocks.pauli.PauliLetter import PauliZ, PauliY, PauliX
from main.building_blocks.Qubit import Qubit
from main.codes.Code import Code
from main.utils.types import Coordinates


class HexagonalCode(Code):
    def __init__(
            self, data_qubits: Dict[Coordinates, Qubit],
            check_schedule: List[List[Check]],
            distance: int = None):
        self.colours = [Red, Green, Blue]
        self.letters = [PauliX, PauliY, PauliZ]
        super().__init__(data_qubits, check_schedule, distance=distance)

    @staticmethod
    def get_neighbour_coords(coords: Tuple[int, int]) -> List[Tuple[int, int]]:
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
    def plaquette_in_shifted_column(plaquette_anchor_x_coord: int):
        return bool(((plaquette_anchor_x_coord - 4) // 6) % 2)

    @staticmethod
    def data_qubit_in_shifted_column(data_qubit_x_coord: int):
        return bool(((data_qubit_x_coord - 2) // 6) % 2)

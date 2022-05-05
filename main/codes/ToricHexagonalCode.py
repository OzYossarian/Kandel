from typing import Tuple, List

from main.Colour import Colour
from main.building_blocks.Qubit import Qubit, Coordinates
from main.codes.HexagonalCode import HexagonalCode
from main.enums import State


class ToricHexagonalCode(HexagonalCode):
    def __init__(self, distance: int):
        self.distance = distance
        self.width = 2 * (8 + 4) * (distance // 4)
        self.height = 3 * 4 * (distance // 4)

        data_qubits = {}
        for x in range(0, self.width, 2):
            if not self.is_plaquette_column(x):
                for y in range(0, self.height, 4):
                    y_shift = 2 if self.data_qubit_in_shifted_column(x) else 0
                    coords = (x, y + y_shift)
                    data_qubits[coords] = Qubit(coords, State.Zero)

        # Leave checks to be defined later.
        super().__init__(data_qubits, [])

    def colourful_plaquette_anchors(self) -> List[Tuple[Coordinates, Colour]]:
        colourful_anchors = []
        for x in range(4, self.width, 6):
            for y in range(2, self.height, 4):
                y_shift = 0
                colour_shift = 0
                if self.plaquette_in_shifted_column(x):
                    y_shift = -2
                    colour_shift = 1
                coords = (x, y + y_shift)
                colour = (((y - 2) // 4) + colour_shift) % 3
                colourful_anchors.append((coords, self.colours[colour]))

        return colourful_anchors

    def wrap_coords(self, coords: Tuple[int, int]):
        (x, y) = coords
        return (x % self.width, y % self.height)


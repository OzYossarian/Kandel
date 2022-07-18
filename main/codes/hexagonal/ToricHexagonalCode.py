from collections import defaultdict
from typing import Tuple, List, Dict

from main.Colour import Colour
from main.building_blocks.Qubit import Qubit, Coordinates
from main.codes.hexagonal.HexagonalCode import HexagonalCode
from main.enums import State


class ToricHexagonalCode(HexagonalCode):
    def __init__(self, distance: int):
        assert distance % 4 == 0
        self.width = 2 * (8 + 4) * (distance // 4)
        self.height = 3 * 4 * (distance // 4)
        self._colourful_plaquette_anchors = None

        data_qubits = {}
        for x in range(0, self.width, 2):
            if not self.is_plaquette_column(x):
                for y in range(0, self.height, 4):
                    y_shift = 2 if self.data_qubit_in_shifted_column(x) else 0
                    coords = (x, y + y_shift)
                    data_qubits[coords] = Qubit(coords)

        # Leave checks to be defined later.
        super().__init__(data_qubits, [], distance)

    @property
    def colourful_plaquette_anchors(self) -> Dict[Colour, Coordinates]:
        if self._colourful_plaquette_anchors is None:
            colourful_anchors = defaultdict(list)
            for x in range(4, self.width, 6):
                for y in range(2, self.height, 4):
                    y_shift = 0
                    colour_shift = 0
                    if self.plaquette_in_shifted_column(x):
                        y_shift = -2
                        colour_shift = 1
                    coords = (x, y + y_shift)
                    colour = (((y - 2) // 4) + colour_shift) % 3
                    colourful_anchors[self.colours[colour]].append(coords)
            self._colourful_plaquette_anchors = colourful_anchors
        return self._colourful_plaquette_anchors

    def wrap_coords(self, coords: Tuple[int, int]):
        (x, y) = coords
        return (x % self.width, y % self.height)


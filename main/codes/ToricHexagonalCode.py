from collections import defaultdict
from typing import Tuple, List, Dict

from main.codes.ToricCode import ToricCode
from main.utils.Colour import Colour
from main.building_blocks.Qubit import Qubit
from main.codes.HexagonalCode import HexagonalCode
from main.utils.types import Coordinates


class ToricHexagonalCode(HexagonalCode, ToricCode):
    def __init__(self, rows: int, columns: int, distance: int = None, **kwargs):
        # Number of columns must be even in order for periodic boundaries
        # to slot together
        assert columns % 2 == 0
        width = (columns // 2) * (8 + 4)
        height = rows * 4

        data_qubits = {}
        for x in range(0, width, 2):
            if not self.is_plaquette_column(x):
                for y in range(0, height, 4):
                    y_shift = 2 if self.is_shifted_column(x) else 0
                    coords = (x, y + y_shift)
                    data_qubits[coords] = Qubit(coords)

        # Leave checks to be defined later.
        super().__init__(
            width=width,
            height=height,
            data_qubits=data_qubits,
            distance=distance,
            **kwargs)

        self._colourful_plaquette_anchors = None
        self._plaquette_anchors = None

    @property
    def colourful_plaquette_anchors(self) -> Dict[Colour, List[Coordinates]]:
        if self._colourful_plaquette_anchors is None:
            self._get_plaquette_anchors()
        return self._colourful_plaquette_anchors

    @property
    def plaquette_anchors(self) -> List[Coordinates]:
        if self._plaquette_anchors is None:
            self._get_plaquette_anchors()
        return self._plaquette_anchors

    def _get_plaquette_anchors(self):
        colourful_anchors = defaultdict(list)
        anchors = []
        for x in range(4, self.width, 6):
            for y in range(2, self.height, 4):
                y_shift = 0
                colour_shift = 0
                if self.is_shifted_column(x):
                    y_shift = -2
                    colour_shift = 1
                coords = (x, y + y_shift)
                colour = (((y - 2) // 4) + colour_shift) % 3
                colourful_anchors[self.colours[colour]].append(coords)
                anchors.append(coords)
        self._colourful_plaquette_anchors = colourful_anchors
        self._plaquette_anchors = anchors


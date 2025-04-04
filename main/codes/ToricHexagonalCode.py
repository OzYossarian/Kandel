from collections import defaultdict
from typing import Tuple, List, Dict

from main.codes.ToricCode import ToricCode
from main.utils.Colour import Colour
from main.building_blocks.Qubit import Qubit
from main.codes.HexagonalCode import HexagonalCode
from main.utils.types import Coordinates


class ToricHexagonalCode(HexagonalCode, ToricCode):
    """Parent class of ToricColourCode and TicTacToeCode.

    Args:
        rows: Number of rows of hexagons.
        columns: Number of columns of hexagons.
        distance: Distance of the code. Defaults to None.
    """
    def __init__(
            self, rows: int, columns: int, distance: int = None, **kwargs):

        if rows <= 0 or columns <= 0:
            raise ValueError(
                f"Number of rows and columns must both be positive! "
                f"Instead, got {rows} rows and {columns} columns.")
        if columns % 2 == 1:
            raise ValueError(
                f"Number of columns of hexagons must be even in order for "
                f"periodic boundaries to slot together. Instead, {columns} "
                f"columns of hexagons were requested.")
        self.rows = rows
        self.columns = columns
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
        if self.rows % 3 != 0:
            raise ValueError(
                f"A toric hexagonal code with {self.rows} rows of hexagons "
                f"is not three-colourable! Number of rows must be a multiple "
                f"of three for the code to have this property.")
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


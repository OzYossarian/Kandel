from typing import Tuple

from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.building_blocks.Operator import Operator
from main.building_blocks.Pauli import PauliX
from main.building_blocks.Check import Check
from main.Colour import Red, Green, Blue
from main.QPUs.QPU import QPU
from main.building_blocks.Qubit import Qubit, Coordinates
from main.codes.HexagonalCode import HexagonalCode
from main.codes.ToricColourCode import ToricColourCode
from main.enums import State, Layout


class TriangularColourCode(HexagonalCode):
    def __init__(self, distance: int, layout: Layout):
        self.distance = distance
        self.width = 3 * (distance // 2)
        if distance % 2 == 0:
            self.width -= 1

        # To avoid duplicating code, create a triangular colour code by just
        # cutting a big chunk out of a toric colour code.
        toric_distance = (1 + (distance // 4)) * 4
        toric_code = ToricColourCode(toric_distance, layout)

        data_qubits = {}
        for coords in toric_code.data_qubits:
            if self._is_in_triangle(coords):
                data_qubits[coords] = toric_code.data_qubits[coords]

        checks = []
        for check in toric_code.schedule[0]:
            if self._is_in_triangle(check.center):
                check.operators = [
                    op for op in check.operators
                    if self._is_in_triangle(op.qubit.coords)]
                checks.append(check)

        super().__init__(data_qubits, [checks], layout)

    def _is_in_triangle(self, coords: Tuple[int, int, int]):
        (g, x, y) = coords
        return y >= 0 and y <= x and y <= (self.width - g) - x



from typing import Tuple

from main.codes.hexagonal.HexagonalCode import HexagonalCode
from main.codes.hexagonal.ToricColourCode import ToricColourCode


class TriangularColourCode(HexagonalCode):
    def __init__(self, distance: int):
        assert distance % 2 == 1
        assert distance >= 3
        self.distance = distance
        self.width = (4 + 8) * (distance // 2)
        self.height = self.width // 2

        # To avoid duplicating code, create a triangular colour code by just
        # cutting a big chunk out of a toric colour code.
        toric_distance = (1 + (distance // 4)) * 4
        toric_code = ToricColourCode(toric_distance)

        data_qubits = {}
        for coords in toric_code.data_qubits:
            if self._is_in_triangle(coords):
                data_qubits[coords] = toric_code.data_qubits[coords]

        checks = []
        for check in toric_code.schedule[0]:
            if self._is_in_triangle(check.anchor):
                check.paulis = [
                    pauli for pauli in check.paulis
                    if self._is_in_triangle(pauli.qubit.coords)]
                checks.append(check)

        super().__init__(data_qubits, [checks])

    def _is_in_triangle(self, coords: Tuple[int, int]):
        (x, y) = coords
        # Triangle formed by three lines - check we're inside each of these.
        return y >= 0 and y <= x - 2 and y <= -x + (2 * self.height + 2)



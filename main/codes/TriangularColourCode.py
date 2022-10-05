from typing import Tuple

from main.building_blocks.Check import Check
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.HexagonalCode import HexagonalCode
from main.codes.ToricColourCode import ToricColourCode


class TriangularColourCode(HexagonalCode):
    def __init__(self, distance: int):
        if distance < 3:
            raise ValueError(
                "Can't instantiate a triangular colour code with distance "
                f"less than three! Given distance was {distance}")
        if distance % 2 == 0:
            raise ValueError(
                "Can't instantiate a triangular colour code with even "
                f"distance! Given distance was {distance}")
        self.width = (4 + 8) * (distance // 2)
        self.height = self.width // 2

        # To avoid duplicating code, create a triangular colour code by just
        # cutting a big chunk out of a toric colour code.
        toric_distance = (1 + (distance // 4)) * 4
        toric_code = ToricColourCode(toric_distance)
        # Shift everything by (-2, 0), so that the bottom left qubit of the
        # triangular colour code we cut out is at (0, 0)
        toric_code.data_qubits = {
            (coords[0] - 2, coords[1]): data_qubit
            for coords, data_qubit in toric_code.data_qubits.items()}
        for coords, data_qubit in toric_code.data_qubits.items():
            data_qubit.coords = coords
        for check in toric_code.checks:
            check.anchor = (check.anchor[0] - 2, check.anchor[1])

        data_qubits = {}
        for coords, data_qubit in toric_code.data_qubits.items():
            if self._is_in_triangle(coords):
                data_qubits[coords] = data_qubit

        checks = []
        for check in toric_code.check_schedule[0]:
            if self._is_in_triangle(check.anchor):
                paulis = {
                    coords: pauli for coords, pauli in check.paulis.items()
                    if self._is_in_triangle(pauli.qubit.coords)}
                checks.append(Check(paulis, check.anchor, check.colour))

        logical_support = [
            (x, 0)
            for i in range((distance + 1) // 2)
            for x in [12 * i, 4 + 12 * i]][:-1]
        logical_x = LogicalOperator([
            Pauli(data_qubits[coords], PauliLetter('X'))
            for coords in logical_support])
        logical_z = LogicalOperator([
            Pauli(data_qubits[coords], PauliLetter('Z'))
            for coords in logical_support])
        logical_qubit = LogicalQubit(x=logical_x, z=logical_z)

        super().__init__(
            data_qubits=data_qubits,
            check_schedule=[checks],
            logical_qubits=[logical_qubit],
            distance=distance)

    def _is_in_triangle(self, coords: Tuple[int, int]):
        (x, y) = coords
        # Triangle formed by three lines - check we're inside each of these.
        return y >= 0 and y <= x and y <= -x + (2 * self.height)

from typing import List

from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.Check import Check
from main.codes.ToricHexagonalCode import ToricHexagonalCode
from main.utils.types import Coordinates
from main.utils.utils import coords_minus


class ToricColourCode(ToricHexagonalCode):
    def __init__(self, distance: int):
        if distance <= 0:
            raise ValueError(
                f"Toric colour code must have positive distance! "
                f"Instead, got distance {distance}")
        if distance % 4 != 0:
            raise ValueError(
                f"Can only instantiate a toric colour code whose distance is a "
                f"multiple of four - instead, got distance {distance}")

        rows = 3 * (distance // 4)
        columns = 4 * (distance // 4)
        super().__init__(
            rows=rows,
            columns=columns,
            distance=distance)

        checks = self._create_checks()
        self.set_schedules([checks])

        logical_qubits = self._create_logical_qubits()
        self.logical_qubits = logical_qubits

    def _create_checks(self):
        checks = []
        for colour in self.colours:
            anchors = self.colourful_plaquette_anchors[colour]
            for anchor in anchors:
                neighbour_coords = self.get_neighbour_coords(anchor)
                relative_coords = [
                    coords_minus(coords, anchor)
                    for coords in neighbour_coords]
                neighbours = [
                    self.data_qubits[self.wrap_coords(coords)]
                    for coords in neighbour_coords]

                x_paulis = {
                    coords: Pauli(qubit, PauliLetter('X'))
                    for coords, qubit in zip(relative_coords, neighbours)}
                z_paulis = {
                    coords: Pauli(qubit, PauliLetter('Z'))
                    for coords, qubit in zip(relative_coords, neighbours)}

                x_check = Check(x_paulis, anchor, colour)
                z_check = Check(z_paulis, anchor, colour)

                checks.append(x_check)
                checks.append(z_check)
        return checks

    def _create_logical_qubits(self):
        horizontal_coords = [
            (x, 0)
            for i in range(self.distance // 2)
            for x in [2 + 12 * i, 6 + 12 * i]]
        vertical_coords = [
            (0, y)
            for i in range(self.distance // 4)
            for y in [2 + 12 * i, 6 + 12 * i]]
        vertical_coords.extend([
            (2, y)
            for i in range(self.distance // 4)
            for y in [0 + 12 * i, 8 + 12 * i]])
        logical_qubits = [
            self._create_logical_qubit(horizontal_coords, vertical_coords),
            self._create_logical_qubit(vertical_coords, horizontal_coords)]
        return logical_qubits

    def _create_logical_qubit(
            self, x_support: List[Coordinates], z_support: List[Coordinates]):
        x = LogicalOperator([
            Pauli(self.data_qubits[coords], PauliLetter('X'))
            for coords in x_support])
        z = LogicalOperator([
            Pauli(self.data_qubits[coords], PauliLetter('Z'))
            for coords in z_support])
        return LogicalQubit(x=x, z=z)


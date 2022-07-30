from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliX, PauliZ
from main.building_blocks.Check import Check
from main.codes.hexagonal.ToricHexagonalCode import ToricHexagonalCode
from main.utils.utils import coords_minus


class ToricColourCode(ToricHexagonalCode):
    def __init__(self, distance: int):
        assert distance % 4 == 0
        rows = 3 * (distance // 4)
        columns = 4 * (distance // 4)
        super().__init__(rows, columns, distance)

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
                    coords: Pauli(qubit, PauliX)
                    for coords, qubit in zip(relative_coords, neighbours)}
                z_paulis = {
                    coords: Pauli(qubit, PauliZ)
                    for coords, qubit in zip(relative_coords, neighbours)}

                x_check = Check(x_paulis, anchor, colour)
                z_check = Check(z_paulis, anchor, colour)

                checks.append(x_check)
                checks.append(z_check)

        self.set_schedules([checks])

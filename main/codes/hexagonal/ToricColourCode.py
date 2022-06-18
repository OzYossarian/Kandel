from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliX, PauliZ
from main.building_blocks.Check import Check
from main.codes.hexagonal.ToricHexagonalCode import ToricHexagonalCode


class ToricColourCode(ToricHexagonalCode):
    def __init__(self, distance: int):
        super().__init__(distance)

        checks = []
        for colour in self.colours:
            anchors = self.colourful_plaquette_anchors[colour]
            for anchor in anchors:
                plaquette_data_qubits = [
                    self.data_qubits[self.wrap_coords(neighbour)]
                    for neighbour in self.get_neighbours(anchor)]

                x_paulis = [
                    Pauli(qubit, PauliX)
                    for qubit in plaquette_data_qubits]
                z_paulis = [
                    Pauli(qubit, PauliZ)
                    for qubit in plaquette_data_qubits]

                x_check = Check(x_paulis, anchor, colour=colour)
                z_check = Check(z_paulis, anchor, colour=colour)

                checks.append(x_check)
                checks.append(z_check)

        self.set_schedule_and_detectors([checks])

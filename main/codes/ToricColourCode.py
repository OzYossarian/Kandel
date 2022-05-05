from main.building_blocks.Pauli import Pauli
from main.building_blocks.PauliLetter import PauliX, PauliZ
from main.building_blocks.Check import Check
from main.codes.ToricHexagonalCode import ToricHexagonalCode


class ToricColourCode(ToricHexagonalCode):
    def __init__(self, distance: int):
        super().__init__(distance)

        checks = []
        for anchor, colour in self.colourful_plaquette_anchors():
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

        self.set_schedule([checks])

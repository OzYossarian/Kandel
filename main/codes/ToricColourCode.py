from main.building_blocks.Operator import Operator
from main.building_blocks.Pauli import PauliX, PauliZ
from main.building_blocks.Check import Check
from main.codes.ToricHexagonalCode import ToricHexagonalCode


class ToricColourCode(ToricHexagonalCode):
    def __init__(self, distance: int):
        super().__init__(distance)

        checks = []
        for center, colour in self.colourful_plaquette_centers():
            plaquette_data_qubits = [
                self.data_qubits[self.wrap_coords(neighbour)]
                for neighbour in self.get_neighbours(center)]

            x_ops = [
                Operator(qubit, PauliX)
                for qubit in plaquette_data_qubits]
            z_ops = [
                Operator(qubit, PauliZ)
                for qubit in plaquette_data_qubits]

            x_stabilizer = Check(x_ops, center, colour=colour)
            z_stabilizer = Check(z_ops, center, colour=colour)

            checks.append(x_stabilizer)
            checks.append(z_stabilizer)

        self.set_schedule([checks])

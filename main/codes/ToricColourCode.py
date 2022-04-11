from main.building_blocks.Operator import Operator
from main.building_blocks.Pauli import PauliX, PauliZ
from main.building_blocks.Check import Check
from main.Colour import Red, Green, Blue
from main.building_blocks.Qubit import Qubit, Coordinates
from main.codes.HexagonalCode import HexagonalCode
from main.enums import State


class ToricColourCode(HexagonalCode):
    def __init__(self, distance: int):
        assert distance % 4 == 0
        self.distance = distance

        self.width = 2 * (8 + 4) * (distance // 4)
        self.height = 3 * 4 * (distance // 4)

        data_qubits = {}
        plaquette_centers = []
        checks = []
        colours = [Red, Green, Blue]

        # Define data qubits
        for x in range(0, self.width, 2):
            if not self.is_plaquette_column(x):
                for y in range(0, self.height, 4):
                    y_shift = 2 if self.data_qubit_in_shifted_column(x) else 0
                    coords = (x, y + y_shift)
                    data_qubits[coords] = Qubit(coords, State.Zero)

        for x in range(4, self.width, 6):
            for y in range(2, self.height, 4):
                y_shift = -2 if self.plaquette_in_shifted_column(x) else 0
                coords = (x, y + y_shift)
                plaquette_centers.append(coords)

        for center in plaquette_centers:
            plaquette_data_qubits = [
                data_qubits[self._wrap_coords(neighbour)]
                for neighbour in self.get_neighbours(center)]

            x_ops = [
                Operator(qubit, PauliX)
                for qubit in plaquette_data_qubits]
            z_ops = [
                Operator(qubit, PauliZ)
                for qubit in plaquette_data_qubits]

            (x, y) = center
            colour = ((y - 2) // 4) % 3
            if self.plaquette_in_shifted_column(x):
                colour = (colour - 1) % 3

            x_stabilizer = Check(x_ops, center, None, colours[colour], None)
            z_stabilizer = Check(z_ops, center, None, colours[colour], None)

            checks.append(x_stabilizer)
            checks.append(z_stabilizer)

        super().__init__(data_qubits, [checks])

    def _wrap_coords(self, coords: Coordinates):
        (x, y) = coords
        return (x % self.width, y % self.height)

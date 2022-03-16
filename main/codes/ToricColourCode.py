from main.building_blocks.Operator import Operator
from main.building_blocks.Pauli import PauliX, PauliZ
from main.building_blocks.Check import Check
from main.Colour import Red, Green, Blue
from main.building_blocks.Qubit import Qubit, Coordinates
from main.codes.HexagonalCode import HexagonalCode
from main.enums import State, Layout


class ToricColourCode(HexagonalCode):
    def __init__(self, distance: int, layout: Layout):
        assert distance % 4 == 0
        self.distance = distance

        self.width = 3 * (distance // 2)
        self.height = 3 * (distance // 4)

        data_qubits = {}
        plaquette_centers = []
        checks = []
        colours = [Red, Green, Blue]

        def define_qubits(grid, plaquette_center_column):
            for x in range(self.width):
                is_plaquette_center_column = x % 3 == plaquette_center_column
                for y in range(self.height):
                    coords = (grid, x, y)
                    if is_plaquette_center_column:
                        plaquette_centers.append(coords)
                    else:
                        data_qubits[coords] = Qubit(coords, State.Zero)

        define_qubits(0, 1)
        define_qubits(1, 2)

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

            (g, x, y) = center
            colour = (y - g) % 3
            x_stabilizer = Check(x_ops, center, None, colours[colour], None)
            z_stabilizer = Check(z_ops, center, None, colours[colour], None)

            checks.append(x_stabilizer)
            checks.append(z_stabilizer)

        super().__init__(data_qubits, [checks], layout)

    def _wrap_coords(self, coords: Coordinates):
        (g, x, y) = coords
        return (g, x % self.width, y % self.height)

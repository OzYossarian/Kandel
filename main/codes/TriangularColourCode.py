from typing import Tuple

from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.building_blocks.Operator import Operator
from main.building_blocks.Pauli import PauliX
from main.building_blocks.Check import Check
from main.Colour import Red, Green, Blue
from main.QPUs.QPU import QPU
from main.building_blocks.Qubit import Qubit, Coordinates
from main.codes.HexagonalCode import HexagonalCode
from main.enums import State, Layout


class TriangularColourCode(HexagonalCode):
    def __init__(self, distance: int, layout: Layout):
        self.distance = distance
        self.layout = layout

        width = 3 * (distance // 2)
        if distance % 2 == 0:
            width -= 1
        data_qubits = {}
        plaquette_centers = []
        checks = []
        colours = [Red, Green, Blue]

        def define_qubits(grid, width_on_grid, plaquette_center_column):
            for x in range(width_on_grid + 1):
                is_plaquette_center_column = x % 3 == plaquette_center_column
                y_max = x if x <= width_on_grid / 2 else width_on_grid - x
                for y in range(0, y_max + 1):
                    coords = (grid, x, y)
                    if is_plaquette_center_column:
                        plaquette_centers.append(coords)
                    else:
                        data_qubits[coords] = Qubit(coords, State.Zero)

        define_qubits(0, width, 1)
        define_qubits(1, width - 1, 2)

        def is_in_triangle(coords: Tuple[int, int, int]):
            (g, x, y) = coords
            return y >= 0 and y <= x and y <= (width - g) - x

        for center in plaquette_centers:
            plaquette_data_qubits = [
                data_qubits[neighbour]
                for neighbour in self.get_neighbours(center)
                if is_in_triangle(neighbour)]

            x_ops = [
                Operator(qubit, PauliX)
                for qubit in plaquette_data_qubits]
            z_ops = [
                Operator(qubit, PauliX)
                for qubit in plaquette_data_qubits]

            (g, x, y) = center
            colour = (y - g) % 3
            x_stabilizer = Check(x_ops, center, None, colours[colour], None)
            z_stabilizer = Check(z_ops, center, None, colours[colour], None)

            checks.append(x_stabilizer)
            checks.append(z_stabilizer)

        super().__init__(data_qubits, [checks], layout)

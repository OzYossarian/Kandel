from typing import Dict
from main.building_blocks.Check import Check
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.Qubit import Qubit
from main.codes.Code import Code
from main.utils.types import Coordinates


class RotatedSurfaceCode(Code):
    """A [d^2, 1, d] version of the surface code.

    See for details: https://errorcorrectionzoo.org/c/rotated_surface

    Args:
        distance: The distance of the code, which also specificies the dimensions of the code.
    """
    def __init__(self, distance: int):
        if distance < 3:
            raise ValueError(
                f"Distance of a rotated surface code should be at least 3!"
                f"Instead, got distance {distance}")
        if distance % 2 == 0:
            raise ValueError(
                f"Currently only implemented for odd distances! "
                f"Instead, got distance {distance}")

        data_qubits = self.init_data_qubits(distance)
        checks = self.init_face_checks(data_qubits, distance)
        boundary_checks = self.init_boundary_checks(data_qubits, distance)
        checks.extend(boundary_checks)
        logical_qubit = self.init_logical_qubit(data_qubits, distance)

        super().__init__(
            data_qubits=data_qubits,
            check_schedule=[checks],
            distance=distance,
            logical_qubits=[logical_qubit])

    def init_data_qubits(self, distance: int):
        data_qubits = dict()
        y_middle = distance - 1

        # diagonal lines of data qubits
        starting_x, starting_y = (0, y_middle)
        for i in range(distance):
            for j in range(distance):
                coords = (starting_x + j, starting_y - j)
                data_qubits[coords] = Qubit(coords)
            starting_x += 1
            starting_y += 1
        return data_qubits

    def init_face_checks(self, data_qubits: Dict[Coordinates, Qubit], distance: int):
        checks = []
        y_middle = distance - 1
        pauli_letters = [PauliLetter('X'), PauliLetter('Z')]
        starting_x, starting_y = (1, y_middle)

        # Diagonal lines of faces
        for _ in range(distance - 1):
            for j in range(distance - 1):
                anchor = (starting_x + j, starting_y - j)
                letter = pauli_letters[anchor[0] % 2]
                paulis = {
                    (1, 0): Pauli(data_qubits[anchor[0] + 1, anchor[1]], letter),
                    (0, 1): Pauli(data_qubits[anchor[0], anchor[1] + 1], letter),
                    (-1, 0): Pauli(data_qubits[anchor[0] - 1, anchor[1]], letter),
                    (0, -1): Pauli(data_qubits[anchor[0], anchor[1] - 1], letter),
                }
                check = Check(paulis, anchor)
                checks.append(check)

            starting_x += 1
            starting_y += 1

        return checks

    def init_boundary_checks(   
        self, data_qubits: Dict[Coordinates, Qubit], distance: int
    ):
        checks = []
        x_middle, y_middle = distance - 1, distance - 1

        for i in range(0, distance // 2):
            # bottom left boundary
            anchor = (2 * i + 1, y_middle - 2 * (i + 1))
            paulis = {
                (1, 0): Pauli(data_qubits[anchor[0] + 1, anchor[1]], PauliLetter('Z')),
                (0, 1): Pauli(data_qubits[anchor[0], anchor[1] + 1], PauliLetter('Z')),
            }
            new_check = Check(paulis, anchor)
            checks.append(new_check)

            # top right boundary
            anchor = (x_middle + 2 * i + 1, 2 * (distance - 1) - 2 * i)
            paulis = {
                (0, -1): Pauli(data_qubits[anchor[0], anchor[1] - 1], PauliLetter('Z')),
                (-1, 0): Pauli(data_qubits[anchor[0] - 1, anchor[1]], PauliLetter('Z')),
            }
            new_check = Check(paulis, anchor)
            checks.append(new_check)

            # top left boundary
            anchor = (2 * i, y_middle + 2 * i + 1)
            paulis = {
                (1, 0): Pauli(data_qubits[anchor[0] + 1, anchor[1]], PauliLetter('X')),
                (0, -1): Pauli(data_qubits[anchor[0], anchor[1] - 1], PauliLetter('X')),
            }
            new_check = Check(paulis, anchor)
            checks.append(new_check)

            # bottom right boundary
            anchor = (x_middle + 2 * (i + 1), 2 * i + 1)
            paulis = {
                (0, 1): Pauli(data_qubits[anchor[0], anchor[1] + 1], PauliLetter('X')),
                (-1, 0): Pauli(data_qubits[anchor[0] - 1, anchor[1]], PauliLetter('X')),
            }
            new_check = Check(paulis, anchor)
            checks.append(new_check)
        return checks

    def init_logical_qubit(self, data_qubits: Dict[Coordinates, Qubit], distance: int):
        # Put logical X along bottom left boundary
        bottom_left = [(i, distance - 1 - i) for i in range(distance)]
        logical_x = LogicalOperator(
            [Pauli(data_qubits[coords], PauliLetter('X')) for coords in bottom_left]
        )

        # Put logical Z along top left boundary
        top_left = [(i, distance - 1 + i) for i in range(distance)]
        logical_z = LogicalOperator(
            [Pauli(data_qubits[coords], PauliLetter('Z')) for coords in top_left]
        )

        return LogicalQubit(x=logical_x, z=logical_z)

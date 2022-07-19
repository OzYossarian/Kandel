from turtle import color
from typing import Dict
from main.building_blocks.Check import Check
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ, PauliX
from main.building_blocks.Qubit import Qubit, Coordinates
from main.codes.Code import Code
from main.enums import State
from main.Colour import Green, Red


class RotatedSurfaceCode(Code):
    def __init__(self, distance: int):
        data_qubits = self.init_data_qubits(distance)
        checks = self.init_face_checks(data_qubits, distance)
        boundary_checks = self.init_boundary_checks(data_qubits, distance)
        checks.extend(boundary_checks)
        logical_qubit = self.init_logical_qubit(data_qubits, distance)

        super().__init__(
            data_qubits, [checks], distance=distance, logical_qubits=[logical_qubit]
        )

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
        pauli_letters = [PauliX, PauliZ]
        letter_to_colour = dict()
        letter_to_colour[PauliX] = Red
        letter_to_colour[PauliZ] = Green
        starting_x, starting_y = (1, y_middle)

        # Diagonal lines of faces
        for i in range(distance - 1):
            for j in range(distance - 1):
                anchor = (starting_x + j, starting_y - j)
                letter = pauli_letters[anchor[0] % 2]

                paulis = [
                    Pauli(data_qubits[anchor[0] + 1, anchor[1]], letter),
                    Pauli(data_qubits[anchor[0], anchor[1] + 1], letter),
                    Pauli(data_qubits[anchor[0] - 1, anchor[1]], letter),
                    Pauli(data_qubits[anchor[0], anchor[1] - 1], letter),
                ]
                # test colour
                check = Check(paulis, anchor, colour=letter_to_colour[letter])
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
            paulis = [
                Pauli(data_qubits[anchor[0] + 1, anchor[1]], PauliZ),
                Pauli(data_qubits[anchor[0], anchor[1] + 1], PauliZ),
            ]
            new_check = Check(paulis, anchor, Green)
            checks.append(new_check)

            # top right boundary
            anchor = (x_middle + 2 * i + 1, 2 * (distance - 1) - 2 * i)
            paulis = [
                Pauli(data_qubits[anchor[0], anchor[1] - 1], PauliZ),
                Pauli(data_qubits[anchor[0] - 1, anchor[1]], PauliZ),
            ]
            new_check = Check(paulis, anchor, colour=Green)
            checks.append(new_check)

            # top left boundary
            anchor = (2 * i, y_middle + 2 * i + 1)
            paulis = [
                Pauli(data_qubits[anchor[0] + 1, anchor[1]], PauliX),
                Pauli(data_qubits[anchor[0], anchor[1] - 1], PauliX),
            ]
            new_check = Check(paulis, anchor, colour=Red)
            checks.append(new_check)

            # bottom right boundary
            anchor = (x_middle + 2 * (i + 1), 2 * i + 1)
            paulis = [
                Pauli(data_qubits[anchor[0], anchor[1] + 1], PauliX),
                Pauli(data_qubits[anchor[0] - 1, anchor[1]], PauliX),
            ]
            new_check = Check(paulis, anchor, colour=Red)
            checks.append(new_check)
        return checks

    def init_logical_qubit(self, data_qubits: Dict[Coordinates, Qubit], distance: int):
        # Put logical X along bottom left boundary
        bottom_left = [(i, distance - 1 - i) for i in range(distance)]
        logical_x = LogicalOperator(
            [Pauli(data_qubits[coords], PauliX) for coords in bottom_left]
        )

        # Put logical Z along top left boundary
        top_left = [(i, distance - 1 + i) for i in range(distance)]
        logical_z = LogicalOperator(
            [Pauli(data_qubits[coords], PauliZ) for coords in top_left]
        )

        return LogicalQubit(logical_x, logical_z)

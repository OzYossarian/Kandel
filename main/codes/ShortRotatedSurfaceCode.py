from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Coordinates, Qubit
from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliX, PauliZ
from main.codes.Code import Code
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from typing import Dict, List

from main.utils.utils import embed_coords


class ShortRotatedSurfaceCode(Code):
    def __init__(self, distance: int) -> Code:
        data_qubits = self.init_data_qubits(distance)
        checks_0, checks_1 = self.init_face_checks(data_qubits, distance)
        boundary_checks_0, boundary_checks_1 = self.init_boundary_checks(
            data_qubits, distance
        )
        checks_0.extend(boundary_checks_0)
        checks_1.extend(boundary_checks_1)
        self.init_check_schedule(checks_0, checks_1)

        logical_qubit = self.init_logical_qubit(data_qubits, distance)

        super().__init__(
            data_qubits,
            [checks_0, checks_1],
            self.detector_schedule,
            distance=distance,
            logical_qubits=[logical_qubit],
        )

    def init_check_schedule(self, checks_0, checks_1):
        self.detector_schedule = [[], []]
        for check in checks_0:
            anchor = (
                embed_coords(check.anchor, check.dimension + 1)
                if check.anchor is not None
                else None
            )
            drum = Drum([(-1, check)], [(0, check)], 0, anchor)
            self.detector_schedule[0].append(drum)

        for check in checks_1:
            anchor = (
                embed_coords(check.anchor, check.dimension + 1)
                if check.anchor is not None
                else None
            )
            drum = Drum([(-1, check)], [(0, check)], 0, anchor)
            self.detector_schedule[1].append(drum)

    def init_data_qubits(self, distance: int) -> dict:
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

    def init_face_checks(
        self, data_qubits: Dict[Coordinates, Qubit], distance: int
    ) -> List:
        checks_0, checks_1 = [], []
        y_middle = distance - 1
        pauli_letters = [PauliX, PauliZ]
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
                if anchor[0] % 2 == 0:
                    checks_0.append(check)
                else:
                    checks_1.append(check)
            starting_x += 1
            starting_y += 1

        return checks_0, checks_1

    def init_boundary_checks(
        self, data_qubits: Dict[Coordinates, Qubit], distance: int
    ) -> List:
        checks_0, checks_1 = [], []
        x_middle, y_middle = distance - 1, distance - 1

        for i in range(0, distance // 2):
            # bottom left boundary
            anchor = (2 * i + 1, y_middle - 2 * (i + 1))
            paulis = {
                (1, 0): Pauli(data_qubits[anchor[0] + 1, anchor[1]], PauliZ),
                (0, 1): Pauli(data_qubits[anchor[0], anchor[1] + 1], PauliZ),
            }
            new_check = Check(paulis, anchor)
            checks_0.append(new_check)

            # top right boundary
            anchor = (x_middle + 2 * i + 1, 2 * (distance - 1) - 2 * i)
            paulis = {
                (0, -1): Pauli(data_qubits[anchor[0], anchor[1] - 1], PauliZ),
                (-1, 0): Pauli(data_qubits[anchor[0] - 1, anchor[1]], PauliZ),
            }
            new_check = Check(paulis, anchor)
            checks_0.append(new_check)

            # top left boundary
            anchor = (2 * i, y_middle + 2 * i + 1)
            paulis = {
                (1, 0): Pauli(data_qubits[anchor[0] + 1, anchor[1]], PauliX),
                (0, -1): Pauli(data_qubits[anchor[0], anchor[1] - 1], PauliX),
            }
            new_check = Check(paulis, anchor)
            checks_1.append(new_check)

            # bottom right boundary
            anchor = (x_middle + 2 * (i + 1), 2 * i + 1)
            paulis = {
                (0, 1): Pauli(data_qubits[anchor[0], anchor[1] + 1], PauliX),
                (-1, 0): Pauli(data_qubits[anchor[0] - 1, anchor[1]], PauliX),
            }
            new_check = Check(paulis, anchor)
            checks_1.append(new_check)
        return checks_0, checks_1

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

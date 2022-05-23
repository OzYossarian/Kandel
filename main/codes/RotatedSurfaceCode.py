from typing import Dict, List, Tuple
from main.building_blocks.Check import Check
from main.building_blocks.Pauli import Pauli
from main.building_blocks.PauliLetter import PauliZ, PauliX
from main.building_blocks.Qubit import Qubit, Coordinates
from main.codes.Code import Code
from main.enums import State


class RotatedSurfaceCode(Code):
    def __init__(self, distance: int):
        data_qubits = self.init_data_qubits(distance)
        ancilla_qubits, checks = self.init_face_checks(data_qubits, distance)
        boundary_ancilla_qubits, boundary_checks = self.init_boundary_checks(
            data_qubits, distance)
        ancilla_qubits.update(boundary_ancilla_qubits)
        checks.extend(boundary_checks)
        # for now just considering one type of logical error and therefore
        # one type of logical operator, this is the logical X operator
        self.logical_operator = [
            Pauli(data_qubits[(distance - 1, i * 2)], PauliX)
            for i in range(distance)]

        super().__init__(data_qubits, [checks], None, ancilla_qubits)

    def init_data_qubits(self, distance: int):
        data_qubits = dict()
        y_middle = distance-1

        # diagonal lines of data qubits
        starting_x, starting_y = (0, y_middle)
        for i in range(distance):
            for j in range(distance):
                coords = (starting_x+j, starting_y-j)
                data_qubits[coords] = Qubit(coords, State(0))
            starting_x += 1
            starting_y += 1
        return data_qubits

    def init_face_checks(self, data_qubits: Dict[Coordinates, Qubit], distance: int):
        ancilla_qubits = dict()
        schedule = []
        y_middle = distance-1
        pauli_letters = [PauliX, PauliZ]
        starting_x, starting_y = (1, y_middle)

        # diagonal lines of ancilla qubits
        for i in range(distance-1):
            for j in range(distance-1):
                (x, y) = (starting_x+j, starting_y-j)
                anchor = (starting_x+j, starting_y-j)
                letter = pauli_letters[x % 2]
                ancilla = Qubit(anchor)
                paulis = [
                    Pauli(data_qubits[anchor[0]+1, anchor[1]], letter),
                    Pauli(data_qubits[anchor[0], anchor[1]+1], letter),
                    Pauli(data_qubits[anchor[0]-1, anchor[1]], letter),
                    Pauli(data_qubits[anchor[0], anchor[1]-1], letter)]
                check = Check(paulis, anchor, ancilla=ancilla)
                schedule.append(check)
                ancilla_qubits[anchor] = ancilla

            starting_x += 1
            starting_y += 1

        return ancilla_qubits, schedule

    def init_boundary_checks(
            self, data_qubits: Dict[Coordinates, Qubit], distance: int):
        ancilla_qubits = dict()
        schedule = []

        x_middle, y_middle = distance-1, distance-1

        for i in range(0, distance//2):
            # bottom left boundary
            anchor = (2*i+1, y_middle-2*(i+1))
            ancilla = Qubit(anchor, State.Zero)
            ancilla_qubits[anchor] = ancilla
            paulis = [
                Pauli(data_qubits[anchor[0] + 1, anchor[1]], PauliZ),
                Pauli(data_qubits[anchor[0], anchor[1] + 1], PauliZ)]
            new_check = Check(paulis, anchor, ancilla=ancilla)
            schedule.append(new_check)

            # top right boundary
            anchor = (x_middle + 2*i + 1, 2*(distance-1) - 2*i)
            ancilla = Qubit(anchor, State.Zero)
            ancilla_qubits[anchor] = ancilla
            paulis = [
                Pauli(data_qubits[anchor[0], anchor[1] - 1], PauliZ),
                Pauli(data_qubits[anchor[0] - 1, anchor[1]], PauliZ)]
            new_check = Check(paulis, anchor, ancilla=ancilla)
            schedule.append(new_check)

            # top left boundary
            anchor = (2*i, y_middle + 2*i+1)
            ancilla = Qubit(anchor, State.Plus)
            ancilla_qubits[anchor] = ancilla
            paulis = [
                Pauli(data_qubits[anchor[0] + 1, anchor[1]], PauliX),
                Pauli(data_qubits[anchor[0], anchor[1] - 1], PauliX)]
            new_check = Check(paulis, anchor, ancilla=ancilla)
            schedule.append(new_check)

            # bottom right boundary
            anchor = (x_middle + 2*(i+1), 2*i + 1)
            ancilla = Qubit(anchor, State.Plus)
            ancilla_qubits[anchor] = ancilla
            paulis = [
                Pauli(data_qubits[anchor[0], anchor[1] + 1], PauliX),
                Pauli(data_qubits[anchor[0] - 1, anchor[1]], PauliX)]
            new_check = Check(paulis, anchor, ancilla=ancilla)
            schedule.append(new_check)
        return ancilla_qubits, schedule

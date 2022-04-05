from typing import Dict

from main.building_blocks.Check import Check
from main.building_blocks.Operator import Operator
from main.building_blocks.Pauli import PauliZ, PauliX
from main.building_blocks.Qubit import Qubit
from main.codes.Code import Code
from main.enums import State
from main.Colour import Red, Green, Blue


class RotatedSurfaceCode(Code):
    def __init__(self, distance):
        data_qubits = self.init_data_qubits(distance)
        ancilla_qubits, checks = self.init_face_checks(data_qubits, distance)
        boundary_ancilla_qubits, boundary_checks = self.init_boundary_checks(
            data_qubits, distance)
        ancilla_qubits.update(boundary_ancilla_qubits)
        print(ancilla_qubits, 'ancilla')
        checks.extend(boundary_checks)
        super().__init__(data_qubits, ancilla_qubits, [checks])

    def init_data_qubits(self, distance: int):
        data_qubits = dict()
        y_middle = distance-1

        # diagonal lines of data qubits
        starting_x, starting_y = (0, y_middle)
        for i in range(distance):
            for j in range(distance):
                data_qubits[(starting_x+j, starting_y-j)
                            ] = Qubit((starting_x+j, starting_y-j), State(0))
            starting_x += 1
            starting_y += 1
        return(data_qubits)

    def init_face_checks(self, data_qubits: [Qubit], distance: int):
        ancilla_qubits = dict()
        schedule = []
        x_middle, y_middle = (distance-1, distance-1)

        # diagonal lines of ancilla qubits
        colours = (Green, Red)

        starting_x, starting_y = (1, y_middle)
        check_type = {Green: PauliZ, Red: PauliX}
        initial_state_map = {Green: State.Zero, Red: State.Plus}
        for i in range(distance-1):
            if i % 2 == 0:
                check_colour = [Green, Red]

            else:
                check_colour = [Red, Green]

            for j in range(distance-1):
                center = (starting_x+j, starting_y-j)

                if j % 2 == 0:
                    # give these a specific order for compilation convenience?
                    ancilla = Qubit(center, initial_state_map[check_colour[0]])
                    operators = [
                        Operator(
                            data_qubits[center[0]+1, center[1]], check_type[check_colour[0]]),
                        Operator(
                            data_qubits[center[0], center[1]+1], check_type[check_colour[0]]),
                        Operator(
                            data_qubits[center[0], center[1]-1], check_type[check_colour[0]]),
                        Operator(
                            data_qubits[center[0]-1, center[1]], check_type[check_colour[0]])]
                    new_check = Check(operators, center,
                                      ancilla, colour=check_colour[0])
                    #print(new_check, 'new check')
                else:
                    ancilla = Qubit(center, initial_state_map[check_colour[1]])
                    operators = [
                        Operator(
                            data_qubits[center[0]+1, center[1]], check_type[check_colour[1]]),
                        Operator(
                            data_qubits[center[0], center[1]-1], check_type[check_colour[1]]),
                        Operator(
                            data_qubits[center[0], center[1]+1], check_type[check_colour[1]]),
                        Operator(
                            data_qubits[center[0]-1, center[1]], check_type[check_colour[1]])]
                    new_check = Check(operators, center,
                                      ancilla, colour=check_colour[1])
                schedule.append(new_check)
                ancilla_qubits[center] = ancilla

            starting_x += 1
            starting_y += 1

        return(ancilla_qubits, schedule)

    def init_boundary_checks(self, data_qubits: [Qubit], distance: int):
        ancilla_qubits = dict()
        schedule = []

        x_middle, y_middle = distance-1, distance-1
        # y_top = d
        for i in range(0, distance//2):
            # bottom left boundary
            center = (2*i+1, y_middle-2*(i+1))
            ancilla = Qubit(center, State.Zero)
            ancilla_qubits[center] = ancilla
            operators = [
                Operator(data_qubits[center[0]+1, center[1]], PauliZ),
                Operator(data_qubits[center[0], center[1]+1], PauliZ)]
            new_check = Check(operators, center, ancilla, colour=Green)
            schedule.append(new_check)

            # top right boundary
            center = (x_middle + 2*i + 1, 2*(distance-1) - 2*i)
            ancilla = Qubit(center, State.Zero)
            ancilla_qubits[center] = ancilla
            operators = [
                Operator(data_qubits[center[0], center[1]-1], PauliZ),
                Operator(data_qubits[center[0]-1, center[1]], PauliZ)]
            new_check = Check(operators, center, ancilla, colour=Green,
                              initialization_timestep=2)
            schedule.append(new_check)

            # top left boundary
            center = (2*i, y_middle + 2*i+1)
            ancilla = Qubit(center, State.Zero)
            ancilla_qubits[center] = ancilla
            operators = [
                Operator(data_qubits[center[0]+1, center[1]], PauliZ),
                Operator(data_qubits[center[0], center[1]-1], PauliZ)]
            new_check = Check(operators, center, ancilla, colour=Red)
            schedule.append(new_check)

            # bottom right boundary
            center = (x_middle + 2*(i+1), 2*i + 1)
            ancilla = Qubit(center, State.Zero)
            ancilla_qubits[center] = ancilla
            operators = [
                Operator(data_qubits[center[0], center[1]+1], PauliZ),
                Operator(data_qubits[center[0]-1, center[1]], PauliZ)]
            new_check = Check(operators, center, ancilla,
                              colour=Red, initialization_timestep=2)
            schedule.append(new_check)
        return(ancilla_qubits, schedule)

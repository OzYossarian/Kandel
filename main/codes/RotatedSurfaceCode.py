from typing import Dict, List, Tuple
from main.building_blocks.Check import Check
from main.building_blocks.Operator import Operator
from main.building_blocks.Pauli import PauliZ, PauliX
from main.building_blocks.Qubit import Qubit
from main.codes.Code import Code
from main.enums import State
from main.Colour import Red, Green


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
            Operator(data_qubits[(distance-1, i*2)], PauliX) for i in range(distance)]

        super().__init__(data_qubits, [checks], ancilla_qubits)

    def init_data_qubits(self, distance: int) -> List[Qubit]:
        """Initializes data qubits

        Args:
            distance (int): distance of the code (width of the lattice)

        Returns:
            List[Qubit]: list of data qubits
        """
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

    def init_face_checks(self, data_qubits: List[Qubit],
                         distance: int) -> Tuple[List[Qubit], List[Check]]:
        """Initializes the non-boundary checks

        Args:
            data_qubits (List[Qubit]): list of data qubits
            distance (int): distance of the code

        Returns:
            Tuple[List[Qubit], List[Check]]: A tuple containing a list of data
                                             qubits and a list of checks
        """
        ancilla_qubits = dict()
        schedule = []
        y_middle = distance-1
        check_colours = [Green, Red]
        check_type = [PauliZ, PauliX]
        initial_state_map = [State.Zero, State.Plus]
        starting_x, starting_y = (1, y_middle)

        # diagonal lines of ancilla qubits
        for i in range(distance-1):
            for j in range(distance-1):
                center = (starting_x+j, starting_y-j)

                if j % 2 == 0:
                    # the operators are in a specific order here to make sure
                    # hook errors don't spread to logicals

                    pauli_op = check_type[i % 2]
                    ancilla = Qubit(
                        center, initial_state_map[i % 2])
                    operators = [
                        Operator(
                            data_qubits[center[0]+1, center[1]], pauli_op),
                        Operator(
                            data_qubits[center[0], center[1]+1], pauli_op),
                        Operator(
                            data_qubits[center[0], center[1]-1], pauli_op),
                        Operator(
                            data_qubits[center[0]-1, center[1]], pauli_op)]
                    new_check = Check(operators, center,
                                      ancilla, colour=check_colours[i % 2],
                                      initialization_timestep=(i+1) % 2)

                else:
                    pauli_op = check_type[(i+1) % 2]
                    ancilla = Qubit(center, initial_state_map[(i+1) % 2])
                    operators = [
                        Operator(
                            data_qubits[center[0]+1, center[1]], pauli_op),
                        Operator(
                            data_qubits[center[0], center[1]-1], pauli_op),
                        Operator(
                            data_qubits[center[0], center[1]+1], pauli_op),
                        Operator(
                            data_qubits[center[0]-1, center[1]], pauli_op)]

                    new_check = Check(operators, center,
                                      ancilla, colour=check_colours[(i+1) % 2],
                                      initialization_timestep=i % 2)
                schedule.append(new_check)
                ancilla_qubits[center] = ancilla

            starting_x += 1
            starting_y += 1

        return(ancilla_qubits, schedule)

    def init_boundary_checks(self, data_qubits: List[Qubit],
                             distance: int) -> Tuple[List[Qubit], List[Check]]:
        """Initializes the boundary checks

        Args:
            data_qubits (List[Qubit]): list of data qubits
            distance (int): distance of the code

        Returns:
            Tuple[List[Qubit], List[Check]]: A tuple containing a list of data
                                             qubits and a list of checks
        """
        ancilla_qubits = dict()
        schedule = []

        x_middle, y_middle = distance-1, distance-1

        for i in range(0, distance//2):
            # bottom left boundary
            center = (2*i+1, y_middle-2*(i+1))
            ancilla = Qubit(center, State.Zero)
            ancilla_qubits[center] = ancilla
            operators = [
                Operator(data_qubits[center[0]+1, center[1]], PauliZ),
                Operator(data_qubits[center[0], center[1]+1], PauliZ)]
            new_check = Check(operators, center, ancilla,
                              colour=Green, initialization_timestep=1)
            schedule.append(new_check)

            # top right boundary
            center = (x_middle + 2*i + 1, 2*(distance-1) - 2*i)
            ancilla = Qubit(center, State.Zero)
            ancilla_qubits[center] = ancilla
            operators = [
                Operator(data_qubits[center[0], center[1]-1], PauliZ),
                Operator(data_qubits[center[0]-1, center[1]], PauliZ)]
            new_check = Check(operators, center, ancilla, colour=Green,
                              initialization_timestep=3)
            schedule.append(new_check)

            # top left boundary
            center = (2*i, y_middle + 2*i+1)
            ancilla = Qubit(center, State.Plus)
            ancilla_qubits[center] = ancilla
            operators = [
                Operator(data_qubits[center[0]+1, center[1]], PauliX),
                Operator(data_qubits[center[0], center[1]-1], PauliX)]
            new_check = Check(operators, center, ancilla,
                              initialization_timestep=0,
                              colour=Red)
            schedule.append(new_check)

            # bottom right boundary
            center = (x_middle + 2*(i+1), 2*i + 1)
            ancilla = Qubit(center, State.Plus)
            ancilla_qubits[center] = ancilla
            operators = [
                Operator(data_qubits[center[0], center[1]+1], PauliX),
                Operator(data_qubits[center[0]-1, center[1]], PauliX)]
            new_check = Check(operators, center, ancilla,
                              colour=Red, initialization_timestep=2)
            schedule.append(new_check)
        return(ancilla_qubits, schedule)

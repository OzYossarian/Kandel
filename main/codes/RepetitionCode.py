from typing import Dict

from main.building_blocks.Check import Check
from main.building_blocks.Operator import Operator
from main.building_blocks.Pauli import PauliZ
from main.building_blocks.Qubit import Qubit
from main.codes.Code import Code
from main.enums import State


class RepetitionCode(Code):
    def __init__(self, distance: int):
        data_qubits, ancilla_qubits, schedule = self.init_checks(distance)
        self.logical_operator = [Operator(data_qubits[0], PauliZ)]
        super().__init__(data_qubits, ancilla_qubits, [schedule])

    def init_checks(self, distance: int):
        data_qubits = {2*i: Qubit(2*i, State.Zero)
                       for i in range(distance)}
        ancilla_qubits = dict()
        schedule = []
        for i in range(distance-1):
            operators = [
                Operator(data_qubits[2*i], PauliZ),
                Operator(data_qubits[2*(i+1)], PauliZ)]
            center = 2*i + 1
            ancilla = Qubit(center, State.Zero)
            ancilla_qubits[center] = ancilla
            new_check = Check(operators, center, ancilla)
            schedule.append(new_check)
        return data_qubits, ancilla_qubits, schedule

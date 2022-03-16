from typing import Dict

from main.building_blocks.Check import Check
from main.building_blocks.Operator import Operator
from main.building_blocks.Pauli import PauliZ
from main.building_blocks.Qubit import Qubit
from main.codes.Code import Code
from main.enums import State


class RepetitionCode(Code):
    def __init__(self, distance: int):
        data_qubits, schedule = self.init_checks(distance)
        super().__init__(data_qubits, [schedule])

    def init_checks(self, distance: int):
        data_qubits = {2*i: Qubit(2*i, State.Zero)
                       for i in range(distance)}
        schedule = []
        for i in range(distance-1):
            operators = [
                Operator(data_qubits[2*i], PauliZ),
                Operator(data_qubits[2*(i+1)], PauliZ)]
            center = 2*i + 1
            ancilla = Qubit(center, State.Zero)
            new_check = Check(operators, center, ancilla)
            schedule.append(new_check)
        return data_qubits, schedule

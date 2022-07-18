from typing import Dict

from main.building_blocks.Check import Check
from main.building_blocks.Operator import Operator
from main.building_blocks.Pauli import PauliZ
from main.building_blocks.Qubit import Qubit
from main.codes.Code import Code
from main.enums import State


class RotatedSurfaceCode(Code):
    def __init__(self, distance):
        data_qubits, ancilla_qubits, schedule = self.init_checks(distance)
        # TODO self.logical_operator = [Operator(data_qubits[0], PauliZ)]
        super().__init__(data_qubits, ancilla_qubits, [schedule])

    def init_checks(self, distance: int):
        data_qubits = dict()
        for i in range(distance):
            for j in range(distance):
                data_qubits[(2*i+1, 2*j+1)] = Qubit((2*i+1, 2*j+1), State.Zero)

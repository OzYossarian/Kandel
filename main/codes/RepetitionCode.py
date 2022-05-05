from typing import Dict

from main.building_blocks.Check import Check
from main.building_blocks.Pauli import Pauli
from main.building_blocks.PauliLetter import PauliZ
from main.building_blocks.Qubit import Qubit
from main.codes.Code import Code
from main.enums import State


class RepetitionCode(Code):
    def __init__(self, distance: int):
        data_qubits, ancilla_qubits, schedule = self.init_checks(distance)
        self.logical_operator = [Pauli(data_qubits[0], PauliZ)]
        super().__init__(data_qubits, [schedule], ancilla_qubits)

    def init_checks(self, distance: int):
        data_qubits = {2*i: Qubit(2*i, State.Zero)
                       for i in range(distance)}
        ancilla_qubits = dict()
        schedule = []
        for i in range(distance-1):
            paulis = [
                Pauli(data_qubits[2 * i], PauliZ),
                Pauli(data_qubits[2 * (i + 1)], PauliZ)]
            anchor = 2*i + 1
            ancilla = Qubit(anchor, State.Zero)
            ancilla_qubits[anchor] = ancilla
            new_check = Check(paulis, anchor, ancilla)
            schedule.append(new_check)
        return data_qubits, ancilla_qubits, schedule

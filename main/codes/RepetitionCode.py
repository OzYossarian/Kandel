from main.building_blocks.Check import Check
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ, PauliX
from main.building_blocks.Qubit import Qubit
from main.codes.Code import Code
from main.enums import State


class RepetitionCode(Code):
    def __init__(self, distance: int):
        data_qubits, checks = self.init_checks(distance)
        logical_x = LogicalOperator([
            Pauli(qubit, PauliX) for qubit in data_qubits])
        logical_z = LogicalOperator([
            Pauli(data_qubits[0], PauliZ)])
        logical_qubit = LogicalQubit(logical_x, logical_z)

        super().__init__(
            data_qubits, [checks], distance=distance,
            logical_qubits=[logical_qubit])

    def init_checks(self, distance: int):
        data_qubits = {2 * i: Qubit(2 * i) for i in range(distance)}
        checks = []
        for i in range(distance-1):
            paulis = [
                Pauli(data_qubits[2 * i], PauliZ),
                Pauli(data_qubits[2 * (i + 1)], PauliZ)]
            anchor = 2*i + 1
            new_check = Check(paulis, anchor)
            checks.append(new_check)
        return data_qubits, checks

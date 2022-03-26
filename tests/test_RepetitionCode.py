from main.building_blocks.Check import Check
from main.building_blocks.Operator import Operator
from main.building_blocks.Pauli import PauliZ
from main.building_blocks.Qubit import Qubit
from main.codes.RepetitionCode import RepetitionCode
from main.enums import State

d3_rep_code = RepetitionCode(3)


def test_init():
    assert(len(d3_rep_code.data_qubits) == 3)
    qubit = d3_rep_code.data_qubits[4]
    assert qubit.coords == 4
    assert qubit.initial_state == State.Zero
    assert d3_rep_code.logical_operator == d3_rep_code.data_qubits[0]


def test_init_checks():
    expected_center = 3
    last_check = d3_rep_code.schedule[0][-1]
    assert last_check.center == expected_center
    check_qubits = {op.qubit for op in last_check.operators}
    expected_qubits = {d3_rep_code.data_qubits[2], d3_rep_code.data_qubits[4]}
    assert check_qubits == expected_qubits
    check_paulis = [op.pauli for op in last_check.operators]
    assert check_paulis == [PauliZ, PauliZ]

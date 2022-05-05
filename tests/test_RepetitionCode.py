from main.building_blocks.Pauli import Pauli
from main.building_blocks.PauliLetter import PauliZ
from main.codes.RepetitionCode import RepetitionCode
from main.enums import State

d3_rep_code = RepetitionCode(3)


def test_init():
    assert(len(d3_rep_code.data_qubits) == 3)
    qubit = d3_rep_code.data_qubits[4]
    assert qubit.coords == 4
    assert qubit.initial_state == State.Zero
    assert d3_rep_code.logical_operator == [
        Pauli(d3_rep_code.data_qubits[0], PauliZ)]


def test_init_checks():
    expected_anchor = 3
    last_check = d3_rep_code.schedule[0][-1]
    assert last_check.anchor == expected_anchor
    check_qubits = {pauli.qubit for pauli in last_check.paulis}
    expected_qubits = {d3_rep_code.data_qubits[2], d3_rep_code.data_qubits[4]}
    assert check_qubits == expected_qubits
    check_paulis = [pauli.letter for pauli in last_check.paulis]
    assert check_paulis == [PauliZ, PauliZ]

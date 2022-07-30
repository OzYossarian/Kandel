from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliX, PauliZ
from main.codes.RepetitionCode import RepetitionCode

d3_rep_code = RepetitionCode(3)


def test_init():
    assert len(d3_rep_code.data_qubits) == 3
    qubit = d3_rep_code.data_qubits[4]
    assert qubit.coords == 4

    assert d3_rep_code.logical_qubits[0].z.at_round(-1) == [
        Pauli(d3_rep_code.data_qubits[0], PauliZ)
    ]

    assert d3_rep_code.logical_qubits[0].x.at_round(-1) == [
        Pauli(d3_rep_code.data_qubits[0], PauliX),
        Pauli(d3_rep_code.data_qubits[2], PauliX),
        Pauli(d3_rep_code.data_qubits[4], PauliX),
    ]


def test_init_checks():
    expected_anchor = 3
    last_check = d3_rep_code.check_schedule[0][-1]
    assert last_check.anchor == expected_anchor
    check_qubits = {pauli.qubit for pauli in last_check.paulis.values()}
    expected_qubits = {d3_rep_code.data_qubits[2], d3_rep_code.data_qubits[4]}
    assert check_qubits == expected_qubits
    check_paulis = [pauli.letter for pauli in last_check.paulis.values()]
    assert check_paulis == [PauliZ, PauliZ]

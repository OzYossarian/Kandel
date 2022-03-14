from main.codes.repetition_code import RepetitionCode
from main.Qubit import Qubit
from main.Code import Code
from main.enums import Pauli, State
from main.Check import Check

d3_rep_code = RepetitionCode(3)


def test_init():
    assert(len(d3_rep_code.data_qubits) == 3)
    assert(d3_rep_code.data_qubits[4] == Qubit(2, State.Zero))


def test_init_checks():
    op = {d3_rep_code.data_qubits[2]: Pauli.Z,
          d3_rep_code.data_qubits[4]: Pauli.Z}
    ancilla = Qubit(3, State.Zero)
    center = 3
    assert d3_rep_code.schedule[-1] == Check(op, ancilla, center)

from main.codes.non_convex_color_codes.k_2_code import K2ColorCode


def test_init():
    K2ColorCode()


def test_create_data_and_ancilla_qubits():
    d3_code = K2ColorCode(3)
    data_qubits, ancilla_qubits = d3_code.create_data_and_ancilla_qubits()
    assert len(data_qubits) == 12
    assert len(ancilla_qubits) == 5


def test_create_checks():
    d3_code = K2ColorCode(3)
    assert len(d3_code.checks) == 10

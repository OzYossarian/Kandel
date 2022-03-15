from main.QPUs.QPU import SquareLatticeQPU


def test_square_lattice_qpu():
    qpu = SquareLatticeQPU((1, 2, 3))
    expected_positions = [
        (0, 0, 0),
        (0, 0, 1),
        (0, 0, 2),
        (0, 1, 0),
        (0, 1, 1),
        (0, 1, 2)
    ]
    actual_positions = list(qpu.qubits)
    assert len(expected_positions) == len(actual_positions)
    assert set(expected_positions) == set(actual_positions)

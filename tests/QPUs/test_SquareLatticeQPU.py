from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.codes.RepetitionCode import RepetitionCode
from main.codes.hexagonal.TriangularColourCode import TriangularColourCode


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


def test_embed_1d_into_1d():
    code = RepetitionCode(4)
    qpu = SquareLatticeQPU((10, ))
    qpu.embed(code, 1, 0)
    for i in range(4):
        assert code.data_qubits[2 * i].coords == 2*i + 1


def test_embed_1d_into_3d():
    code = RepetitionCode(4)
    qpu = SquareLatticeQPU((10, 10, 10))
    qpu.embed(code, (1, 1, 1), 2)
    for i in range(4):
        assert code.data_qubits[2*i].coords == (1, 1, 1 + 2*i)


def test_embed_2d_into_3d():
    code = TriangularColourCode(3)
    qpu = SquareLatticeQPU((30, 30, 30))
    plaquette_anchors = {check.anchor for check in code.checks}
    qubit_coords = {qubit.coords for qubit in code.data_qubits.values()}

    qpu.embed(code, (1, 1, 1), (1, 2))
    expected_anchors = {(1, 1+x, 1+y) for (x, y) in plaquette_anchors}
    assert expected_anchors == {check.anchor for check in code.checks}
    expected_coords = {(1, 1+x, 1+y) for (x, y) in qubit_coords}
    actual_coords = {qubit.coords for qubit in code.data_qubits.values()}
    assert expected_coords == actual_coords

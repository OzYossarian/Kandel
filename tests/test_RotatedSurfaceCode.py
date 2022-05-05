from main.Colour import Green, Red
from main.building_blocks.Pauli import Pauli
from main.building_blocks.PauliLetter import PauliX, PauliZ
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
import pytest

d3_sc = RotatedSurfaceCode(3)
d5_sc = RotatedSurfaceCode(5)
d7_sc = RotatedSurfaceCode(7)


def test_init():
    assert list(d3_sc.ancilla_qubits.keys()) == [
        (1, 2), (2, 1), (2, 3), (3, 2), (1, 0), (3, 4), (0, 3), (4, 1)]
    assert len(list(d5_sc.ancilla_qubits)) == 24
    assert len(d3_sc.schedule[0]) == 8
    assert len(d5_sc.schedule[0]) == 24


def test_data_qubits():
    assert list(d3_sc.data_qubits.keys()) == [
        (0, 2), (1, 1), (2, 0), (1, 3), (2, 2), (3, 1), (2, 4), (3, 3), (4, 2)]
    print(d3_sc.data_qubits[(1, 1)])


def test_ancilla_qubits():
    print(d3_sc.ancilla_qubits.keys())
    assert list(d3_sc.ancilla_qubits.keys()) == [(
        1, 2), (2, 1), (2, 3), (3, 2), (1, 0), (3, 4), (0, 3), (4, 1)]


@pytest.mark.parametrize("code, distance", [(d3_sc, 3), (d5_sc, 5), (d7_sc, 7)])
def test_init_face_checks(code, distance):
    face_ancillas, checks = code.init_face_checks(code.data_qubits, distance)

    # check_0 is the leftmost face check. CNOT dance order is taken from
    # https://arxiv.org/pdf/1612.08208.pdf
    pauli_1 = Pauli(code.data_qubits[(2, distance - 1)], PauliZ)
    pauli_2 = Pauli(code.data_qubits[(1, distance)], PauliZ)
    pauli_3 = Pauli(code.data_qubits[(1, distance - 2)], PauliZ)
    pauli_4 = Pauli(code.data_qubits[(0, distance - 1)], PauliZ)
    assert checks[0].anchor == (1, distance - 1)
    assert checks[0].colour == Green
    assert checks[0].ancilla == face_ancillas[(1, distance-1)]
    assert checks[0].paulis[0].qubit == code.data_qubits[(2, distance - 1)]
    assert checks[0].paulis == [pauli_1, pauli_2, pauli_3, pauli_4]


def test_init_face_checks_bottom():
    # check_1 is the bottom face check
    face_ancillas, checks = d3_sc.init_face_checks(d3_sc.data_qubits, 3)
    pauli_1 = Pauli(d3_sc.data_qubits[(3, 1)], PauliX)
    pauli_2 = Pauli(d3_sc.data_qubits[(2, 0)], PauliX)
    pauli_3 = Pauli(d3_sc.data_qubits[(2, 2)], PauliX)
    pauli_4 = Pauli(d3_sc.data_qubits[(1, 1)], PauliX)
    assert checks[1].anchor == (2, 1)
    assert checks[1].colour == Red
    assert checks[1].ancilla == face_ancillas[(2, 1)]

    assert checks[1].paulis == [pauli_1, pauli_2, pauli_3, pauli_4]


def test_init_boundary_checks():
    # bottom left boundary
    boundary_ancillas, checks = d3_sc.init_boundary_checks(
        d3_sc.data_qubits, 3)
    assert list(boundary_ancillas.keys()) == [(1, 0), (3, 4), (0, 3), (4, 1)]
    pauli_1 = Pauli(d3_sc.data_qubits[(2, 0)], PauliZ)
    pauli_2 = Pauli(d3_sc.data_qubits[(1, 1)], PauliZ)
    assert checks[0].anchor == (1, 0)
    assert checks[0].colour == Green
    assert checks[0].ancilla == boundary_ancillas[(1, 0)]
    assert checks[0].paulis[0].qubit == d3_sc.data_qubits[(2, 0)]
    assert checks[0].paulis == [pauli_1, pauli_2]

    assert checks[0].initialization_timestep == 1
    assert checks[1].initialization_timestep == 3
    assert checks[2].initialization_timestep == 0
    assert checks[3].initialization_timestep == 2


def test_logical_operator():
    d3_logical_op = [Pauli(d3_sc.data_qubits[(2, 0)], PauliX, ),
                     Pauli(d3_sc.data_qubits[(2, 2)], PauliX, ),
                     Pauli(d3_sc.data_qubits[(2, 4)], PauliX, )]
    assert d3_sc.logical_operator == d3_logical_op

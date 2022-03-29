from main.building_blocks.Check import Check
from main.building_blocks.Operator import Operator
from main.building_blocks.Pauli import PauliZ
from main.building_blocks.Qubit import Qubit
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.enums import State

d3_sc = RotatedSurfaceCode(3)
d5_sc = RotatedSurfaceCode(5)


def test_init():
    assert list(d3_sc.ancilla_qubits.keys()) == [
        (1, 2), (2, 1), (2, 3), (3, 2), (1, 0), (3, 4), (0, 3), (4, 1)]
    assert len(list(d5_sc.ancilla_qubits)) == 24
    assert len(d3_sc.ancilla_qubits.schedule) == 24


def test_data_qubits():
    assert list(d3_sc.data_qubits.keys()) == [
        (0, 2), (1, 1), (2, 0), (1, 3), (2, 2), (3, 1), (2, 4), (3, 3), (4, 2)]


def test_init_checks():
    face_ancillas, checks = d3_sc.init_face_checks(d3_sc.data_qubits, 3)

    assert list(face_ancillas.keys()) == [(1, 2), (2, 1), (2, 3), (3, 2)]


test_init_checks()

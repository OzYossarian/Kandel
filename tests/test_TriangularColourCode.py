from main.codes.TriangularColourCode import TriangularColourCode
from main.enums import Layout


def test_distance_3_triangular_colour_code():
    colour_code = TriangularColourCode(3, Layout.Hexagonal)
    assert len(colour_code.schedule) == 1
    assert len(colour_code.checks) == 2 * 3

    plaquette_centers = {check.center for check in colour_code.checks}
    assert plaquette_centers == {(0, 1, 0), (0, 1, 1), (1, 2, 0)}

    data_qubit_coords = set(colour_code.data_qubits.keys())
    assert data_qubit_coords == {
        (0, 0, 0),
        (1, 0, 0),
        (1, 1, 0),
        (1, 1, 1),
        (0, 2, 0),
        (0, 2, 1),
        (0, 3, 0)}

    plaquette_weights = {len(check.operators) for check in colour_code.checks}
    assert plaquette_weights == {4}


def test_distance_4_triangular_colour_code():
    colour_code = TriangularColourCode(4, Layout.Hexagonal)
    assert len(colour_code.data_qubits) == 14
    assert len(colour_code.schedule) == 1
    assert len(colour_code.checks) == 2*7
    plaquette_centers = {check.center for check in colour_code.checks}
    assert len(plaquette_centers) == 7
    plaquette_weights = {len(check.operators) for check in colour_code.checks}
    assert plaquette_weights == {2, 4, 6}


def test_distance_5_triangular_colour_code():
    colour_code = TriangularColourCode(5, Layout.Hexagonal)
    assert len(colour_code.data_qubits) == 19
    assert len(colour_code.schedule) == 1
    assert len(colour_code.checks) == 2*9
    plaquette_centers = {check.center for check in colour_code.checks}
    assert len(plaquette_centers) == 9
    plaquette_weights = {len(check.operators) for check in colour_code.checks}
    assert plaquette_weights == {4, 6}

from main.codes.TriangularColourCode import TriangularColourCode


def test_distance_3_triangular_colour_code():
    colour_code = TriangularColourCode(3)
    assert len(colour_code.schedule) == 1
    assert len(colour_code.checks) == 2 * 3

    plaquette_centers = {check.center for check in colour_code.checks}
    assert plaquette_centers == {(4, 2), (10, 4), (10, 0)}

    data_qubit_coords = set(colour_code.data_qubits.keys())
    assert data_qubit_coords == {
        (2, 0),
        (6, 0),
        (6, 4),
        (8, 2),
        (8, 6),
        (12, 2),
        (14, 0)}

    plaquette_weights = {len(check.operators) for check in colour_code.checks}
    assert plaquette_weights == {4}


def test_distance_5_triangular_colour_code():
    colour_code = TriangularColourCode(5)
    assert len(colour_code.data_qubits) == 19
    assert len(colour_code.schedule) == 1
    assert len(colour_code.checks) == 2*9
    plaquette_centers = {check.center for check in colour_code.checks}
    assert len(plaquette_centers) == 9
    plaquette_weights = {len(check.operators) for check in colour_code.checks}
    assert plaquette_weights == {4, 6}

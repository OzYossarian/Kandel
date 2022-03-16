from main.codes.TriangularColourCode import TriangularColourCode
from main.enums import Layout


def test_triangular_colour_code():
    colour_code_5 = TriangularColourCode(5, Layout.Hexagonal)
    assert len(colour_code_5.data_qubits) == 22
    assert len(colour_code_5.schedule) == 1
    assert len(colour_code_5.checks) == 2*9
    plaquette_centers = {check.center for check in colour_code_5.checks}
    assert len(plaquette_centers) == 9
    plaquette_weights = {len(check.operators) for check in colour_code_5.checks}
    assert plaquette_weights == {4, 6}

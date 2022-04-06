from main.codes.ToricColourCode import ToricColourCode
from main.enums import Layout


def test_distance_4_toric_colour_code():
    colour_code = ToricColourCode(4, Layout.Hexagonal)
    assert len(colour_code.checks) == 2 * 12
    data_qubit_coords = {
        qubit.coords for qubit in colour_code.data_qubits.values()}
    expected_coords = {
        (0, x, y)
        for x in range(6)
        for y in range(3)
        if x % 3 != 1}
    expected_coords.update({
        (1, x, y)
        for x in range(6)
        for y in range(3)
        if x % 3 != 2})
    assert data_qubit_coords == expected_coords

    plaquette_centers = {check.center for check in colour_code.checks}
    expected_centers = {
        (0, x, y)
        for x in [1, 4]
        for y in range(3)}
    expected_centers.update({
        (1, x, y)
        for x in [2, 5]
        for y in range(3)})
    assert plaquette_centers == expected_centers

    for check in colour_code.checks:
        neighbours = colour_code.get_neighbours(check.center)
        expected_coords = {
            colour_code._wrap_coords(coords) for coords in neighbours}
        check_qubit_coords = {
            operator.qubit.coords for operator in check.operators}
        assert expected_coords == check_qubit_coords


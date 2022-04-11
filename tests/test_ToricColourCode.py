from main.codes.ToricColourCode import ToricColourCode


def test_distance_4_toric_colour_code():
    colour_code = ToricColourCode(4)
    assert len(colour_code.checks) == 2 * 12
    data_qubit_coords = {
        qubit.coords for qubit in colour_code.data_qubits.values()}
    expected_coords = {
        (x, y)
        for x in [2, 6, 14, 18]
        for y in [0, 4, 8]}
    expected_coords.update({
        (x, y)
        for x in [0, 8, 12, 20]
        for y in [2, 6, 10]})
    assert data_qubit_coords == expected_coords

    plaquette_centers = {check.center for check in colour_code.checks}
    expected_centers = {
        (x, y)
        for x in [4, 16]
        for y in [2, 6, 10]}
    expected_centers.update({
        (x, y)
        for x in [10, 22]
        for y in [0, 4, 8]})
    assert plaquette_centers == expected_centers

    for check in colour_code.checks:
        neighbours = colour_code.get_neighbours(check.center)
        expected_coords = {
            colour_code._wrap_coords(coords) for coords in neighbours}
        check_qubit_coords = {
            operator.qubit.coords for operator in check.operators}
        assert expected_coords == check_qubit_coords


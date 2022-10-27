import random
from collections import defaultdict

import pytest

from main.codes.ToricHexagonalCode import ToricHexagonalCode
from main.utils.Colour import Blue, Green, Red


def test_toric_hexagonal_code_fails_if_rows_or_columns_zero():
    expected_error = "Number of rows and columns must both be positive"
    with pytest.raises(ValueError, match=expected_error):
        ToricHexagonalCode(rows=0, columns=0)
    with pytest.raises(ValueError, match=expected_error):
        ToricHexagonalCode(rows=0, columns=2)
    with pytest.raises(ValueError, match=expected_error):
        ToricHexagonalCode(rows=2, columns=0)


def test_toric_hexagonal_code_fails_if_columns_odd():
    expected_error = "Number of columns of hexagons must be even"
    for columns in range(1, 25, 2):
        with pytest.raises(ValueError, match=expected_error):
            ToricHexagonalCode(3, columns)


def test_toric_hexagonal_code_not_three_colourable_if_rows_not_multiple_of_three():
    expected_error = "Number of rows must be a multiple of three"
    for rows in [x for x in range(1, 25) if x % 3 != 0]:
        columns = random.choice(range(2, 25, 2))
        code = ToricHexagonalCode(rows, columns)
        with pytest.raises(ValueError, match=expected_error):
            _ = code.colourful_plaquette_anchors


def test_toric_hexagonal_code_init_data_qubits():
    for rows in range(1, 25):
        for columns in range(2, 25, 2):
            expected_coords = set()
            for i in range(columns):
                # Build a zig zag column of coords.
                e = 1 if i % 2 == 0 else -1
                for y in range(0, 4 * rows, 2):
                    x = 1 + e + 6 * i
                    expected_coords.add((x, y))
                    e *= -1

            code = ToricHexagonalCode(rows, columns)
            coords = {
                data_qubit.coords for data_qubit in code.data_qubits.values()}
            assert coords == expected_coords


def test_toric_hexagonal_code_plaquette_anchors():
    colours = [Green, Red, Blue]
    for rows in range(1, 25):
        for columns in range(2, 25, 2):
            expected_colourful_anchors = defaultdict(set)
            e = 3
            for j in range(2 * rows):
                for i in range(columns // 2):
                    x = 7 + e + 12 * i
                    y = 2 * j
                    expected_colourful_anchors[colours[j % 3]].add((x, y))
                e *= -1
            expected_anchors = {
                anchor
                for colour in colours
                for anchor in expected_colourful_anchors[colour]}

            code = ToricHexagonalCode(rows, columns)
            assert set(code.plaquette_anchors) == expected_anchors
            if rows % 3 == 0:
                for colour in colours:
                    result = set(code.colourful_plaquette_anchors[colour])
                    expected = expected_colourful_anchors[colour]
                    assert result == expected

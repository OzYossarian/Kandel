from typing import Tuple

import pytest

from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.pauli.PauliWord import PauliWord
from main.codes.TriangularColourCode import TriangularColourCode


def test_triangular_colour_code_fails_if_distance_less_than_three():
    expected_error = \
        "Can't instantiate a triangular colour code with distance less " \
        "than three"
    for distance in [0, 1, 2]:
        with pytest.raises(ValueError, match=expected_error):
            TriangularColourCode(distance)


def test_triangular_colour_code_fails_if_distance_even():
    expected_error = \
        "Can't instantiate a triangular colour code with even distance"
    for distance in range(4, 25, 2):
        if distance % 2 != 0:
            with pytest.raises(ValueError, match=expected_error):
                TriangularColourCode(distance)


def test_triangular_colour_code_distance_set_correctly_otherwise():
    for distance in range(3, 25, 2):
        code = TriangularColourCode(distance)
        assert code.distance == distance


def test_triangular_colour_code_schedules():
    for distance in range(3, 25, 2):
        code = TriangularColourCode(distance)
        toric_distance = (1 + (distance // 4)) * 4

        # First figure out expected anchors if this was a toric colour code...
        expected_plaquette_anchors = {
            (2 + 12 * i, 2 + 4 * j)
            for i in range(toric_distance // 2)
            for j in range((toric_distance // 4) * 3)}
        expected_plaquette_anchors.update({
            (8 + 12 * i, 4 * j)
            for i in range(toric_distance // 2)
            for j in range((toric_distance // 4) * 3)})
        # ... then restrict to the triangle we cut out.
        expected_plaquette_anchors = {
            anchor for anchor in expected_plaquette_anchors
            if is_in_triangle(anchor, distance)}
        expected_num_checks = 2 * len(expected_plaquette_anchors)

        # Assert check schedule has right shape
        assert len(code.check_schedule) == 1
        assert len(code.check_schedule[0]) == expected_num_checks
        # Assert detector schedule has right shape
        assert len(code.detector_schedule) == 1
        assert len(code.detector_schedule[0]) == expected_num_checks

        for expected_plaquette_anchor in expected_plaquette_anchors:
            # Assert there's an X-check and Z-check at each anchor
            checks = [
                check for check in code.check_schedule[0]
                if check.anchor == expected_plaquette_anchor]
            assert len(checks) == 2
            expected_weight = 4 \
                if is_on_boundary(expected_plaquette_anchor, distance) \
                else 6
            expected_words = {
                PauliWord('X' * expected_weight),
                PauliWord('Z' * expected_weight)}
            assert {check.product.word for check in checks} == expected_words

            # Assert there's an X-detector and Z-detector at each anchor
            expected_detector_anchor = \
                (expected_plaquette_anchor[0], expected_plaquette_anchor[1], 0)
            drums = [
                detector for detector in code.detector_schedule[0]
                if detector.anchor == expected_detector_anchor]
            assert len(drums) == 2
            floor_words = {drum.floor_product.word for drum in drums}
            lid_words = {drum.lid_product.word for drum in drums}
            assert floor_words == expected_words
            assert lid_words == expected_words


def test_triangular_colour_code_logical_qubits():
    for distance in range(3, 25, 2):
        code = TriangularColourCode(distance)
        assert len(code.logical_qubits) == 1

        support = [
            (x, 0)
            for i in range((distance + 1) // 2)
            for x in [12 * i, 4 + 12 * i]][:-1]
        expected_x = [
            Pauli(code.data_qubits[coords], PauliLetter('X'))
            for coords in support]
        expected_z = [
            Pauli(code.data_qubits[coords], PauliLetter('Z'))
            for coords in support]
        assert code.logical_qubits[0].x.at_round(-1) == expected_x
        assert code.logical_qubits[0].z.at_round(-1) == expected_z


def test_triangular_colour_code_dimension():
    for distance in range(3, 25, 2):
        code = TriangularColourCode(distance)
        assert code.dimension == 2


def is_in_triangle(coords: Tuple[int, int], distance: int):
    (x, y) = coords
    height = ((4 + 8) * (distance // 2)) // 2
    # Triangle formed by three lines - check we're inside each of these.
    return y >= 0 and y <= x and y <= -x + (2 * height)


def is_on_boundary(coords: Tuple[int, int], distance: int):
    (x, y) = coords
    height = ((4 + 8) * (distance // 2)) // 2
    # Triangle formed by three lines - check if we're on any of these.
    return y == 0 or y == x or y == -x + (2 * height)

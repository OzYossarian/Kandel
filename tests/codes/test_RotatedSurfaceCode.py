import random
import pytest
from typing import Tuple

from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.pauli.PauliWord import PauliWord
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from tests.utils.utils_numbers import default_test_repeats_small


def test_rotated_surface_code_fails_if_distance_less_than_3():
    expected_error = "Distance of a rotated surface code should be at least 3"
    repeats = default_test_repeats_small
    for distance in random.choices(range(1, -100, -1), k=repeats):
        with pytest.raises(ValueError, match=expected_error):
            RotatedSurfaceCode(distance)


def test_rotated_surface_code_fails_if_distance_even():
    expected_error = "Distance of a rotated surface code should be odd"
    repeats = default_test_repeats_small
    for distance in random.choices(range(4, 100, 2), k=repeats):
        with pytest.raises(ValueError, match=expected_error):
            RotatedSurfaceCode(distance)


def test_rotated_surface_code_init_data_qubits():
    repeats = default_test_repeats_small
    for distance in random.choices(range(3, 25, 2), k=repeats):
        code = RotatedSurfaceCode(distance)
        mid = (distance - 1, distance - 1)
        expected_coords = {
            (x, y)
            for x in range(2 * distance - 1)
            for y in range(2 * distance - 1)
            if (x + y) % 2 == 0 and manhattan((x, y), mid) < distance}
        coords = {
            data_qubit.coords for data_qubit in code.data_qubits.values()}
        assert coords == expected_coords


def test_rotated_surface_code_init_schedules():
    repeats = default_test_repeats_small
    for distance in random.choices(range(3, 25, 2), k=repeats):
        code = RotatedSurfaceCode(distance)

        # Assert schedules have the right shape
        expected_num_checks = (distance - 1) * (distance + 1)
        assert len(code.check_schedule) == 1
        assert len(code.check_schedule[0]) == expected_num_checks
        assert len(code.detector_schedule) == 1
        assert len(code.detector_schedule[0]) == expected_num_checks

        def validate_anchor(anchor, expected_word):
            checks = [
                check for check in code.checks if check.anchor == anchor]
            assert len(checks) == 1
            assert checks[0].product.word == expected_word

            drums = [
                drum for drum in code.detectors
                if drum.anchor == (anchor[0], anchor[1], 0)]
            assert len(drums) == 1
            assert drums[0].floor == [(-1, checks[0])]
            assert drums[0].lid == [(-0, checks[0])]

        # Assert individual checks and drums are as expected.
        # First, bulk checks.
        mid = (distance - 1, distance - 1)
        bulk_anchors = {
            (x, y)
            for x in range(2 * distance - 1)
            for y in range(2 * distance - 1)
            if (x + y) % 2 == 1 and manhattan((x, y), mid) < distance}
        for anchor in bulk_anchors:
            expected_word = PauliWord('XXXX') \
                if anchor[0] % 2 == 0 \
                else PauliWord('ZZZZ')
            validate_anchor(anchor, expected_word)

        # Then XX boundary checks.
        top_left_anchors = [
            (0 + 2*i, distance + 2*i)
            for i in range((distance - 1) // 2)]
        bottom_right_anchors = [
            (2 * (distance - 1) - 2*i, distance - 2 - 2*i)
            for i in range((distance - 1) // 2)]
        for anchor in top_left_anchors + bottom_right_anchors:
            validate_anchor(anchor, PauliWord('XX'))

        # Then ZZ boundary checks.
        bottom_left_anchors = [
            (distance - 2 - 2*i, 0 + 2*i)
            for i in range((distance - 1) // 2)]
        top_right_anchors = [
            (distance + 2 * i, 2 * (distance - 1) - 2 * i)
            for i in range((distance - 1) // 2)]
        for anchor in bottom_left_anchors + top_right_anchors:
            validate_anchor(anchor, PauliWord('ZZ'))


def test_rotated_surface_code_init_logical_qubits():
    repeats = default_test_repeats_small
    for distance in random.choices(range(3, 25, 2), k=repeats):
        code = RotatedSurfaceCode(distance)
        assert len(code.logical_qubits) == 1

        expected_x_support = [
            (i, distance - 1 - i) for i in range(distance)]
        expected_x = [
            Pauli(code.data_qubits[coord], PauliLetter('X'))
            for coord in expected_x_support]
        expected_z_support = [
            (i, distance - 1 + i) for i in range(distance)]
        expected_z = [
            Pauli(code.data_qubits[coord], PauliLetter('Z'))
            for coord in expected_z_support]

        assert code.logical_qubits[0].x.at_round(-1) == expected_x
        assert code.logical_qubits[0].z.at_round(-1) == expected_z


def manhattan(a: Tuple[int, ...], b: Tuple[int, ...]):
    return sum(map(lambda pair: abs(pair[0]-pair[1]), zip(a, b)))


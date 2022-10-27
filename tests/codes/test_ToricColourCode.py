import pytest

from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.pauli.PauliWord import PauliWord
from main.codes.ToricColourCode import ToricColourCode


def test_toric_colour_code_fails_if_distance_not_positive():
    expected_error = \
        "Toric colour code must have positive distance"
    for distance in range(0, -10, -1):
        with pytest.raises(ValueError, match=expected_error):
            ToricColourCode(0)


def test_toric_colour_code_fails_if_distance_not_multiple_of_4():
    expected_error = \
        "Can only instantiate a toric colour whose distance is a multiple " \
        "of four"
    for distance in range(1, 50):
        if distance % 4 != 0:
            with pytest.raises(ValueError, match=expected_error):
                ToricColourCode(distance)


def test_toric_colour_code_distance_set_correctly_otherwise():
    for distance in range(4, 25, 4):
        code = ToricColourCode(distance)
        assert code.distance == distance


def test_toric_colour_code_schedules():
    for distance in range(4, 25, 4):
        code = ToricColourCode(distance)

        expected_plaquette_anchors = {
            (4 + 12 * i, 2 + 4 * j)
            for i in range(distance // 2)
            for j in range((distance // 4) * 3)}
        expected_plaquette_anchors.update({
            (10 + 12 * i, 4 * j)
            for i in range(distance // 2)
            for j in range((distance // 4) * 3)})
        expected_num_checks = 2 * len(expected_plaquette_anchors)

        # Assert check schedule has right shape
        assert len(code.check_schedule) == 1
        assert len(code.check_schedule[0]) == expected_num_checks

        # Assert there's an X-check and Z-check at each anchor
        for expected_anchor in expected_plaquette_anchors:
            checks = [
                check for check in code.check_schedule[0]
                if check.anchor == expected_anchor]
            assert len(checks) == 2
            expected_words = {
                PauliWord('XXXXXX'), PauliWord('ZZZZZZ')}
            assert {check.product.word for check in checks} == expected_words

        expected_detector_anchors = {
            (x, y, 0) for (x, y) in expected_plaquette_anchors}
        # Assert detector schedule has right shape
        assert len(code.detector_schedule) == 1
        assert len(code.detector_schedule[0]) == expected_num_checks

        # Check there's an X-detector and Z-detector at each anchor
        for expected_anchor in expected_detector_anchors:
            drums = [
                detector for detector in code.detector_schedule[0]
                if detector.anchor == expected_anchor]
            assert len(drums) == 2
            expected_words = {
                PauliWord('XXXXXX'), PauliWord('ZZZZZZ')}
            floor_words = {detector.floor_product.word for detector in drums}
            lid_words = {detector.lid_product.word for detector in drums}
            assert floor_words == expected_words
            assert lid_words == expected_words


def test_toric_colour_code_logical_qubits():
    for distance in range(4, 25, 4):
        code = ToricColourCode(distance)
        assert len(code.logical_qubits) == 2

        horizontal_coords = [
            (x, 0)
            for i in range(distance // 2)
            for x in [2 + 12 * i, 6 + 12 * i]]
        vertical_coords = [
            (0, y)
            for i in range(distance // 4)
            for y in [2 + 12 * i, 6 + 12 * i]]
        vertical_coords.extend([
            (2, y)
            for i in range(distance // 4)
            for y in [0 + 12 * i, 8 + 12 * i]])

        expected_x_0 = [
            Pauli(code.data_qubits[coords], PauliLetter('X'))
            for coords in horizontal_coords]
        expected_z_0 = [
            Pauli(code.data_qubits[coords], PauliLetter('Z'))
            for coords in vertical_coords]
        assert code.logical_qubits[0].x.at_round(-1) == expected_x_0
        assert code.logical_qubits[0].z.at_round(-1) == expected_z_0

        expected_x_1 = [
            Pauli(code.data_qubits[coords], PauliLetter('X'))
            for coords in vertical_coords]
        expected_z_1 = [
            Pauli(code.data_qubits[coords], PauliLetter('Z'))
            for coords in horizontal_coords]
        assert code.logical_qubits[1].x.at_round(-1) == expected_x_1
        assert code.logical_qubits[1].z.at_round(-1) == expected_z_1


def test_toric_colour_code_dimension():
    for distance in range(4, 25, 4):
        code = ToricColourCode(distance)
        assert code.dimension == 2

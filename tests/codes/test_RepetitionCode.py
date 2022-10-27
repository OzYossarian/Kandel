import random
from collections import Counter

import pytest

from main.building_blocks.Check import Check
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.RepetitionCode import RepetitionCode
from tests.utils.utils_numbers import default_test_repeats_small


def test_repetition_code_fails_if_distance_less_than_2():
    expected_error = "Repetition code should have distance at least 2"
    # Pick a few random numbers less than 2:
    k = default_test_repeats_small
    for distance in random.choices(range(1, -100, -1), k=k):
        with pytest.raises(ValueError, match=expected_error):
            RepetitionCode(distance)


def test_repetition_code_data_qubits():
    # Pick a few random distances:
    k = default_test_repeats_small
    for distance in random.choices(range(2, 100), k=k):
        code = RepetitionCode(distance)
        qubit_coords = [qubit.coords for qubit in code.data_qubits.values()]
        expected = [2*i for i in range(distance)]
        # Order irrelevant, so don't use a list for comparison.
        # But a set would hide duplicates. So use a counter.
        assert Counter(qubit_coords) == Counter(expected)


def test_repetition_code_schedules():
    # Pick a few random distances:
    k = default_test_repeats_small
    for distance in random.choices(range(2, 100), k=k):
        code = RepetitionCode(distance)

        # Assert schedules have the right shape
        assert len(code.check_schedule) == 1
        assert len(code.check_schedule[0]) == distance - 1
        assert len(code.detector_schedule) == 1
        assert len(code.detector_schedule[0]) == distance - 1

        # Assert individual checks and detectors are as expected
        for i in range(distance - 1):
            checks = [
                check for check in code.checks
                if check.anchor == 1 + 2*i]
            assert len(checks) == 1
            assert checks[0] == Check([
                Pauli(code.data_qubits[2 * i], PauliLetter('Z')),
                Pauli(code.data_qubits[2 * (i + 1)], PauliLetter('Z'))])

            drums = [
                drum for drum in code.detectors
                if drum.anchor == (1 + 2 * i, 0)]
            assert len(drums) == 1
            assert drums[0].floor == [(-1, checks[0])]
            assert drums[0].lid == [(0, checks[0])]


def test_repetition_code_logical_qubits():
    # Pick a few random distances:
    k = default_test_repeats_small
    for distance in random.choices(range(2, 100), k=k):
        code = RepetitionCode(distance)

        assert len(code.logical_qubits) == 1

        expected_z = [
            Pauli(code.data_qubits[0], PauliLetter('Z'))]
        expected_x = [
            Pauli(code.data_qubits[2*i], PauliLetter('X'))
            for i in range(distance)]

        assert code.logical_qubits[0].z.at_round(-1) == expected_z
        assert code.logical_qubits[0].x.at_round(-1) == expected_x

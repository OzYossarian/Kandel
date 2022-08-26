import random
from collections import Counter

import pytest

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliX
from tests.utils.checks import random_checks
from tests.utils.numbers import default_test_repeats_medium, default_test_repeats_small


def test_drum_fails_given_empty_lid():
    expected_error = "Drum lid must contain at least one check"
    lid = []
    floor = [(-1, Check([Pauli(Qubit(0), PauliX)]))]
    with pytest.raises(ValueError, match=expected_error):
        _ = Drum(floor, lid, end=0)


def test_drum_fails_given_empty_floor():
    expected_error = "Drum floor must contain at least one check"
    lid = [(0, Check([Pauli(Qubit(0), PauliX)]))]
    floor = []
    with pytest.raises(ValueError, match=expected_error):
        _ = Drum(floor, lid, end=0)


def test_drum_fails_if_no_lid_check_with_time_component_0():
    expected_error = \
        "At least one check in a Drum's lid must have time component 0"

    # Explicit test
    qubit = Qubit(0)
    check = Check([Pauli(qubit, PauliX)])
    floor = [(-2, check)]
    lid = [(-1, check)]
    with pytest.raises(ValueError, match=expected_error):
        _ = Drum(floor, lid, end=0)

    # Random tests
    for _ in range(default_test_repeats_medium):
        # Use the same checks twice for the floor and lid
        num_checks = random.randint(1, 10)
        dimension = random.randint(1, 10)
        max_weight = 10
        checks = random_checks(
            num_checks,
            int_coords=True,
            max_weight=max_weight,
            dimension=dimension)

        lid_times = random.choices(range(-10, 0), k=num_checks)
        # Keep floor times in the same order so that the floor and lid
        # have the same product.
        offset = random.randint(1, 10)
        floor_times = [t - offset for t in lid_times]
        floor = [(t, check) for t, check in zip(floor_times, checks)]
        lid = [(t, check) for t, check in zip(lid_times, checks)]

        end = random.randint(0, 10)
        with pytest.raises(ValueError, match=expected_error):
            _ = Drum(floor, lid, end)


def test_drum_floor_start_and_end_and_lid_start_and_end():
    # Explicit test
    qubits = [Qubit(0), Qubit(1)]
    checks = [
        Check([Pauli(qubits[0], PauliX)]),
        Check([Pauli(qubits[1], PauliX)])]
    lid = [(0, checks[0]), (-1, checks[1])]
    floor = [(-2, checks[0]), (-3, checks[1])]

    for end in range(default_test_repeats_small):
        drum = Drum(floor, lid, end, anchor=0)
        assert drum.lid_end == end
        assert drum.lid_start == end - 1
        assert drum.floor_end == end - 2
        assert drum.floor_start == end - 3

    # Random tests
    for _ in range(default_test_repeats_small):
        # Use the same checks twice for the floor and lid
        num_checks = random.randint(1, 10)
        dimension = random.randint(1, 10)
        max_weight = 10
        checks = random_checks(
            num_checks,
            int_coords=True,
            max_weight=max_weight,
            dimension=dimension)

        for _ in range(default_test_repeats_small):
            lid_times = random.choices(range(-10, 1), k=num_checks - 1)
            # At least one lid time must be 0.
            lid_times.append(0)
            # Keep floor times in the same order so that the floor and lid
            # have the same product.
            offset = random.randint(1, 10)
            floor_times = [t - offset for t in lid_times]

            floor = [(t, check) for t, check in zip(floor_times, checks)]
            lid = [(t, check) for t, check in zip(lid_times, checks)]

            end = random.randint(0, 10)
            drum = Drum(floor, lid, end)
            assert drum.lid_end == end
            assert drum.lid_start == end + min(lid_times)
            assert drum.floor_end == end + max(floor_times)
            assert drum.floor_start == end + min(floor_times)


def test_drum_has_open_lid():
    # Explicit tests. Use Counters throughout for comparisons because we
    # want to compare lists but don't care about ordering.
    qubits = [Qubit(0), Qubit(1)]
    checks = [
        Check([Pauli(qubits[0], PauliX)]),
        Check([Pauli(qubits[1], PauliX)])]
    lid = [(0, checks[0]), (-1, checks[1])]
    floor = [(-2, checks[0]), (-3, checks[1])]

    schedule_length = 6
    # First test - drum sits entirely within one layer of the schedule
    # 0       1       2       3       4       5       Absolute round
    # |-------|-------|-------|-------|-------|-------
    # 0       1       2       3       4       5       Relative round
    #         floor   floor   lid     lid
    #         start   end     start   end
    end = 4
    drum = Drum(floor, lid, end)
    # Drum should only have an open lid for round in [2, 3]
    for relative_round in [0, 1, 4, 5]:
        has_open_lid, checks_measured = drum.has_open_lid(
            relative_round, schedule_length)
        assert not has_open_lid

    # In round 2, should have an open lid and only floor measured
    has_open_lid, checks_measured = drum.has_open_lid(2, schedule_length)
    assert has_open_lid
    assert Counter(checks_measured) == Counter(floor)

    # In round 3, should have an open lid, and floor and half the
    # lid should be measured.
    has_open_lid, checks_measured = drum.has_open_lid(3, schedule_length)
    assert has_open_lid
    assert Counter(checks_measured) == Counter(floor + [lid[1]])

    # Next test: drum straddles two layers of the code schedule
    # 6       7       8       9       10      11      Absolute round
    # |-------|-------|-------|-------|-------|-------
    # 0       1       2       3       4       5       Relative round
    # lid     lid                     floor   floor
    # start   end                     start   end
    end = 1
    drum = Drum(floor, lid, end)
    # Drum should only have an open lid for round in [5, 6, 11].
    # In particular, shouldn't have an open lid in round 0
    for relative_round in set(range(12)).difference({5, 6, 11}):
        has_open_lid, checks_measured = drum.has_open_lid(
            relative_round, schedule_length)
        assert not has_open_lid

    # In rounds 5 and 11, should have an open lid and only floor measured
    for round in [5, 11]:
        has_open_lid, checks_measured = drum.has_open_lid(
            round, schedule_length)
        assert has_open_lid
        assert Counter(checks_measured) == Counter(floor)

    # In round 6, should have an open lid, and floor and half the
    # lid should be measured.
    has_open_lid, checks_measured = drum.has_open_lid(6, schedule_length)
    assert has_open_lid
    assert Counter(checks_measured) == Counter(floor + [lid[1]])


def test_drum_checks_at_or_after():
    # Explicit tests. Use Counters throughout for comparisons because we
    # want to compare lists but don't care about ordering.
    qubits = [Qubit(0), Qubit(1)]
    checks = [
        Check([Pauli(qubits[0], PauliX)]),
        Check([Pauli(qubits[1], PauliX)])]
    lid = [(0, checks[0]), (-1, checks[1])]
    floor = [(-2, checks[0]), (-3, checks[1])]

    schedule_length = 6
    # First test - drum sits entirely within one layer of the schedule
    # 0       1       2       3       4       5       Absolute round
    # |-------|-------|-------|-------|-------|-------
    # 0       1       2       3       4       5       Relative round
    #         floor   floor   lid     lid
    #         start   end     start   end
    end = 4
    drum = Drum(floor, lid, end)

    for relative_round in [5, 0, 1]:
        timed_checks = drum.checks_at_or_after(
            relative_round, schedule_length)
        assert Counter(timed_checks) == Counter(floor + lid)

    timed_checks = drum.checks_at_or_after(2, schedule_length)
    assert Counter(timed_checks) == Counter([floor[0]] + lid)

    timed_checks = drum.checks_at_or_after(3, schedule_length)
    assert Counter(timed_checks) == Counter(lid)

    timed_checks = drum.checks_at_or_after(4, schedule_length)
    assert Counter(timed_checks) == Counter([lid[0]])

    # Next test: drum straddles two layers of the code schedule
    # 6       7       8       9       10      11      Absolute round
    # |-------|-------|-------|-------|-------|-------
    # 0       1       2       3       4       5       Relative round
    # lid     lid                     floor   floor
    # start   end                     start   end
    end = 1
    drum = Drum(floor, lid, end)

    for relative_round in [2, 3, 4, 8, 9, 10]:
        timed_checks = drum.checks_at_or_after(
            relative_round, schedule_length)
        assert Counter(timed_checks) == Counter(floor + lid)

    for relative_round in [5, 11]:
        timed_checks = drum.checks_at_or_after(
            relative_round, schedule_length)
        assert Counter(timed_checks) == Counter([floor[0]] + lid)

    for relative_round in [0, 6]:
        timed_checks = drum.checks_at_or_after(
            relative_round, schedule_length)
        assert Counter(timed_checks) == Counter(lid)

    for relative_round in [1, 7]:
        timed_checks = drum.checks_at_or_after(
            relative_round, schedule_length)
        assert Counter(timed_checks) == Counter([lid[0]])


def test_drum_repr():
    # Explicit test:
    qubits = [Qubit(0), Qubit(1)]
    checks = [
        Check([Pauli(qubits[0], PauliX)]),
        Check([Pauli(qubits[1], PauliX)])]
    lid = [(0, checks[0]), (-1, checks[1])]
    floor = [(-2, checks[0]), (-3, checks[1])]
    end = 0
    drum = Drum(floor, lid, end)
    expected = {
        'floor_product.word': drum.floor_product.word,
        'lid_product.word': drum.lid_product.word,
        'end': end,
        'floor': floor,
        'lid': lid}
    assert str(drum) == str(expected)

    # Random tests
    for _ in range(default_test_repeats_small):
        # Use the same checks twice for the floor and lid
        num_checks = random.randint(1, 10)
        dimension = random.randint(1, 10)
        max_weight = 10
        checks = random_checks(
            num_checks,
            int_coords=True,
            max_weight=max_weight,
            dimension=dimension)

        lid_times = random.choices(range(-10, 1), k=num_checks - 1)
        # At least one lid time must be 0.
        lid_times.append(0)
        # Keep floor times in the same order so that the floor and lid
        # have the same product.
        offset = random.randint(1, 10)
        floor_times = [t - offset for t in lid_times]

        floor = [(t, check) for t, check in zip(floor_times, checks)]
        lid = [(t, check) for t, check in zip(lid_times, checks)]

        end = random.randint(0, 10)
        drum = Drum(floor, lid, end)
        expected = {
            'floor_product.word': drum.floor_product.word,
            'lid_product.word': drum.lid_product.word,
            'end': end,
            'floor': floor,
            'lid': lid}
        assert str(drum) == str(expected)

import random
import statistics

import pytest

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.detectors.Detector import Detector
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliX, PauliLetter, PauliY, PauliZ
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.utils.utils import modulo_duplicates
from tests.building_blocks.utils_checks import random_checks
from tests.utils.utils_numbers import default_test_repeats_medium, default_test_repeats_small


def test_detector_fails_given_empty_list_of_timed_checks():
    expected_error = "Detector must contain at least one check"
    with pytest.raises(ValueError, match=expected_error):
        _ = Detector([], 0, 0)


def test_detector_fails_if_no_timed_check_happens_end_round():
    expected_error = "At least one timed check must have time component 0"

    # One explicit test:
    check = Check([Pauli(Qubit(0), PauliX)])
    timed_checks = [(-1, check)]
    with pytest.raises(ValueError, match=expected_error):
        _ = Detector(timed_checks, end=0, anchor=0)

    # And some random ones:
    for _ in range(default_test_repeats_medium):
        n = random.randint(1, 100)
        dimension = random.randint(1, 10)
        max_weight = 10
        checks = random_checks(
            n,
            int_coords=True,
            dimension=dimension,
            max_weight=max_weight)

        times = random.choices(range(-10, 0), k=n)
        timed_checks = [(t, check) for t, check in zip(times, checks)]
        end = random.randint(0, 100)
        anchor = tuple(0 for _ in range(dimension))
        with pytest.raises(ValueError, match=expected_error):
            _ = Detector(timed_checks, end, anchor)


def test_detector_fails_if_any_timed_check_positive():
    expected_error = "No timed check can have time component > 0"

    # One explicit test:
    check = Check([Pauli(Qubit(0), PauliX)])
    timed_checks = [(0, check), (1, check)]
    with pytest.raises(ValueError, match=expected_error):
        _ = Detector(timed_checks, end=0, anchor=0)

    # And some random ones:
    for _ in range(default_test_repeats_medium):
        # Need n >= 2 here; need at least one check at time 0 and at least
        # one at a positive time.
        n = random.randint(2, 100)
        dimension = random.randint(1, 10)
        max_weight = 10
        checks = random_checks(
            n,
            int_coords=True,
            dimension=dimension,
            max_weight=max_weight)

        times = random.choices(range(-10, 1), k=n-1)
        # At least one time needs to be 0
        times.append(0)

        # Pick some random times to be positive (but exclude the one we
        # specifically just set to 0)
        num_positive_times = random.randint(1, n-1)
        positive_time_indexes = random.sample(
            range(n-1), k=num_positive_times)
        for i in positive_time_indexes:
            times[i] = random.randint(1, 100)

        timed_checks = [(t, check) for t, check in zip(times, checks)]
        end = random.randint(0, 100)
        anchor = tuple(0 for _ in range(dimension))
        with pytest.raises(ValueError, match=expected_error):
            _ = Detector(timed_checks, end, anchor)


def test_detector_fails_if_check_dims_unequal():
    expected_error = \
        "All checks in a detector must have the same dimension"

    # One explicit test:
    check_dim_1 = Check([Pauli(Qubit((0,)), PauliX)])
    check_dim_2 = Check([Pauli(Qubit((0, 0)), PauliX)])
    timed_checks = [(0, check_dim_1), (0, check_dim_2)]
    with pytest.raises(ValueError, match=expected_error):
        _ = Detector(timed_checks, end=0, anchor=None)

    # And some random ones:
    for _ in range(default_test_repeats_medium):
        n = random.randint(1, 100)
        max_dimension = 10
        max_weight = 10
        checks = random_checks(
            n,
            int_coords=True,
            max_dimension=max_dimension,
            max_weight=max_weight)

        dims = [check.dimension for check in checks]
        if len(set(dims)) > 1:
            times = random.choices(range(-10, 1), k=n-1)
            # At least one time needs to be 0
            times.append(0)
            timed_checks = [(t, check) for t, check in zip(times, checks)]
            end = random.randint(0, 100)
            anchor = None
            with pytest.raises(ValueError, match=expected_error):
                _ = Detector(timed_checks, end, anchor)


def test_detector_fails_if_check_coords_types_unequal():
    expected_error = "Can't mix tuple and non-tuple coordinates"

    # One explicit test:
    tuple_check = Check([Pauli(Qubit((0,)), PauliX)])
    non_tuple_check = Check([Pauli(Qubit(0), PauliX)])
    timed_checks = [(0, tuple_check), (0, non_tuple_check)]
    with pytest.raises(ValueError, match=expected_error):
        _ = Detector(timed_checks, end=0, anchor=None)

    # And some random ones:
    for _ in range(default_test_repeats_medium):
        max_weight = 10
        tuple_n = random.randint(1, 50)
        non_tuple_n = random.randint(1, 50)
        tuple_checks = random_checks(
            tuple_n,
            int_coords=True,
            dimension=1,
            max_weight=max_weight)
        non_tuple_checks = random_checks(
            non_tuple_n,
            int_coords=True,
            tuple_coords=False,
            max_weight=max_weight)

        n = tuple_n + non_tuple_n
        checks = tuple_checks + non_tuple_checks
        times = random.choices(range(-10, 1), k=n-1)
        # At least one time needs to be 0
        times.append(0)
        timed_checks = [(t, check) for t, check in zip(times, checks)]
        end = random.randint(0, 100)
        anchor = None
        with pytest.raises(ValueError, match=expected_error):
            _ = Detector(timed_checks, end, anchor)


def test_anchor_default_tuple_coords():
    # One explicit test:
    checks = [
        Check([Pauli(Qubit((0, 0)), PauliX)]),
        Check([Pauli(Qubit((0, 2)), PauliX)]),
        Check([Pauli(Qubit((2, 0)), PauliX)]),
        Check([Pauli(Qubit((2, 2)), PauliX)])]
    timed_checks = [(0, check) for check in checks]
    detector = Detector(timed_checks, end=0)
    assert detector.anchor == (1, 1)

    # And some random ones:
    for _ in range(default_test_repeats_medium):
        n = random.randint(1, 100)
        dimension = random.randint(1, 10)
        max_weight = 10
        checks = random_checks(
            n,
            int_coords=True,
            dimension=dimension,
            max_weight=max_weight)
        midpoint = tuple([
            statistics.mean([check.anchor[d] for check in checks])
            for d in range(dimension)])

        times = random.choices(range(-10, 1), k=n - 1)
        # At least one time needs to be 0
        times.append(0)
        timed_checks = [(t, check) for t, check in zip(times, checks)]
        end = random.randint(0, 100)
        detector = Detector(timed_checks, end)

        assert detector.anchor == midpoint


def test_anchor_default_non_tuple_coords():
    # One explicit test:
    checks = [
        Check([Pauli(Qubit(0), PauliX)]),
        Check([Pauli(Qubit(1), PauliX)]),
        Check([Pauli(Qubit(2), PauliX)])]
    timed_checks = [(0, check) for check in checks]
    detector = Detector(timed_checks, end=0)
    assert detector.anchor == 1

    # And some random ones:
    for _ in range(default_test_repeats_medium):
        n = random.randint(1, 100)
        max_weight = 10
        checks = random_checks(
            n,
            int_coords=True,
            tuple_coords=False,
            max_weight=max_weight)
        midpoint = statistics.mean([check.anchor for check in checks])

        times = random.choices(range(-10, 1), k=n - 1)
        # At least one time needs to be 0
        times.append(0)
        timed_checks = [(t, check) for t, check in zip(times, checks)]
        end = random.randint(0, 100)
        detector = Detector(timed_checks, end)

        assert detector.anchor == midpoint


# TODO - do we actually want to enforce anything on the sign of the
#  total product? For Checks, yes - one shouldn't measure
#  non-Hermitian things. For Detectors, I'm not so sure?


def test_detector_timed_checks_product():
    # Explicit example:
    qubits = [Qubit(i) for i in range(3)]
    timed_checks = [
        (0, Check([Pauli(qubits[0], PauliX)])),
        (0, Check([Pauli(qubits[1], PauliX)])),
        (0, Check([Pauli(qubits[2], PauliX)])),
        (-1, Check([Pauli(qubits[1], PauliY)])),
        (-1, Check([Pauli(qubits[2], PauliY)])),
        (-2, Check([Pauli(qubits[2], PauliZ)]))]
    detector = Detector(timed_checks, 0, 0)

    # Note XY = iZ and XYZ = iZZ = iI
    expected = PauliProduct([
        Pauli(qubits[0], PauliX),
        Pauli(qubits[1], PauliLetter('Z', 1j)),
        Pauli(qubits[2], PauliLetter('I', 1j))])
    assert detector.product == expected



def test_detector_start_and_end():
    # One explicit example:
    qubit = Qubit(0)
    timed_checks = [
        (0, Check([Pauli(qubit, PauliX)])),
        (-1, Check([Pauli(qubit, PauliX)])),
        (-2, Check([Pauli(qubit, PauliX)]))]
    for end in range(10):
        detector = Detector(timed_checks, end, anchor=0)
        assert detector.start == end - 2
        assert detector.end == end

    # And some random ones:
    for _ in range(default_test_repeats_medium):
        n = random.randint(1, 100)
        max_weight = 10
        checks = random_checks(
            n,
            int_coords=True,
            tuple_coords=False,
            max_weight=max_weight)

        times = random.choices(range(-10, 1), k=n-1)
        # At least one time needs to be 0
        times.append(0)
        timed_checks = [(t, check) for t, check in zip(times, checks)]
        end = random.randint(0, 100)
        detector = Detector(timed_checks, end)

        assert detector.start == end + min(times)
        assert detector.end == end


def test_detector_final_checks():
    # One explicit example:
    qubits = [Qubit(0), Qubit(1)]
    checks = [
        Check([Pauli(qubits[0], PauliX)]),
        Check([Pauli(qubits[1], PauliX)])]
    timed_checks = [
        (0, checks[0]),
        (0, checks[1]),
        (-1, checks[0]),
        (-1, checks[1])]
    detector = Detector(timed_checks, end=0, anchor=0)
    assert detector.final_checks == checks

    # And some random ones:
    for _ in range(default_test_repeats_medium):
        n = random.randint(1, 100)
        max_weight = 10
        checks = random_checks(
            n,
            int_coords=True,
            tuple_coords=False,
            max_weight=max_weight)

        times = random.choices(range(-10, 1), k=n-1)
        # At least one time needs to be 0
        times.append(0)
        timed_checks = [(t, check) for t, check in zip(times, checks)]
        end = random.randint(0, 100)
        detector = Detector(timed_checks, end)

        expected_final_checks = [check for t, check in timed_checks if t == 0]
        assert detector.final_checks == expected_final_checks


def test_detector_timed_checks_mod_2():
    # One explicit example:
    qubits = [Qubit(0), Qubit(1)]
    checks = [
        Check([Pauli(qubits[0], PauliX)]),
        Check([Pauli(qubits[1], PauliX)])]
    timed_checks = [
        (0, checks[0]),
        (-1, checks[1]),
        (-1, checks[1]),
        (-2, checks[0])]
    detector = Detector(timed_checks, end=0, anchor=0)
    assert detector.timed_checks_mod_2 == [
        (0, checks[0]),
        (-2, checks[0])]

    # And some random ones:
    for _ in range(default_test_repeats_medium):
        n = random.randint(1, 100)
        max_weight = 10
        checks = random_checks(
            n,
            int_coords=True,
            tuple_coords=False,
            max_weight=max_weight)

        times = random.choices(range(-10, 1), k=n-1)
        # At least one time needs to be 0
        times.append(0)
        timed_checks = [(t, check) for t, check in zip(times, checks)]
        end = random.randint(0, 100)
        detector = Detector(timed_checks, end)

        # This test relies on modulo duplicates being tested.
        expected = modulo_duplicates(timed_checks, 2)
        assert detector.timed_checks_mod_2 == expected


def test_detector_repr():
    # One explicit test:
    timed_checks = [(0, Check([Pauli(Qubit(0), PauliX)]))]
    detector = Detector(timed_checks, end=0, anchor=0)
    expected = {
        'product.word': detector.product.word,
        'end': 0,
        'timed_checks': timed_checks}
    assert str(detector) == str(expected)

    # Random tests:
    for _ in range(default_test_repeats_small):
        n = random.randint(1, 100)
        max_weight = 10
        checks = random_checks(
            n,
            int_coords=True,
            tuple_coords=False,
            max_weight=max_weight)

        times = random.choices(range(-10, 1), k=n-1)
        # At least one time needs to be 0
        times.append(0)
        timed_checks = [(t, check) for t, check in zip(times, checks)]
        end = random.randint(0, 100)
        detector = Detector(timed_checks, end)

        expected = {
            'product.word': detector.product.word,
            'end': end,
            'timed_checks': timed_checks}
        assert str(detector) == str(expected)

import random
from collections import defaultdict
from typing import Dict, Tuple

import pytest
import stim
from pytest_mock import MockerFixture

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.detectors.Detector import Detector
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.Instruction import Instruction
from main.compiling.Measurer import Measurer
from tests.building_blocks.detectors.utils_detectors import random_detectors
from tests.building_blocks.logical.utils_logical_operators import random_logical_operator
from tests.building_blocks.utils_checks import specific_check, random_checks
from tests.utils.utils_numbers import default_test_repeats_small, default_test_repeats_medium


def test_measurer_add_measurement(mocker: MockerFixture):
    measurer = Measurer()

    measurement = mocker.Mock(spec=Instruction)
    measurement.is_measurement = True
    check = mocker.Mock(spec=Check)
    round = 0

    measurer.add_measurement(measurement, check, round)
    expected = {measurement: (check, round)}
    assert measurer.measurement_checks == expected


def test_measurer_add_detectors():
    measurer = Measurer()

    # Explicit test:
    check_1 = specific_check(['X', 'X'])
    check_2 = specific_check(['Z', 'Z'])
    detector = Detector([(-1, check_1), (0, check_2)], end=0)

    round = 10
    measurer.add_detectors([detector], round)
    expected = {(check_2, round): [detector]}
    assert measurer.triggers == expected

    # Random tests:
    for _ in range(default_test_repeats_small):
        measurer = Measurer()
        num_detectors = random.randint(1, 10)
        dimension = random.randint(1, 10)
        detectors = random_detectors(
            num_detectors,
            int_coords=True,
            max_checks_per_detector=10,
            max_checks_weight=10,
            dimension=dimension)
        round = random.randint(0, 100)
        measurer.add_detectors(detectors, round)
        final_checkss = [
            [check for t, check in detector.timed_checks if t == 0]
            for detector in detectors]
        expected = defaultdict(list)
        for detector, final_checks in zip(detectors, final_checkss):
            for check in final_checks:
                expected[(check, round)].append(detector)
        assert measurer.triggers == expected


def test_measurer_multiply_observable(mocker: MockerFixture):
    measurer = Measurer()
    num_checks = random.randint(0, 10)
    checks = [mocker.Mock(spec=Check) for _ in range(num_checks)]
    observable = mocker.Mock(spec=LogicalOperator)
    round = 0

    measurer.multiply_observable(checks, observable, round)

    expected = {(check, round): [observable] for check in checks}
    assert measurer.triggers == expected


def test_measurer_reset_compilation(mocker: MockerFixture):
    measurer = Measurer()
    measurer.measurement_numbers = mocker.Mock(
        spec=Dict[Tuple[Check, int], int])
    measurer.detectors_compiled = mocker.Mock(spec=Dict[Tuple[int], bool])
    measurer.total_measurements = random.randint(0, 100)

    measurer.reset_compilation()
    assert measurer.measurement_numbers == {}
    assert measurer.detectors_compiled == {}
    assert measurer.total_measurements == 0


def test_measurer_observable_index(mocker: MockerFixture):
    measurer = Measurer()

    observable = mocker.Mock(spec=LogicalOperator)
    # Assert an index gets assigned to this observable, and that this
    # doesn't change if we ask for the same observable's index again later
    assert measurer.observable_index(observable) == 0
    assert measurer.observable_index(observable) == 0

    # Now repeat for some other observable.
    another_observable = mocker.Mock(spec=LogicalOperator)
    assert measurer.observable_index(another_observable) == 1
    assert measurer.observable_index(another_observable) == 1


def test_measurer_measurement_target_fails_if_check_not_yet_measured(mocker: MockerFixture):
    measurer = Measurer()
    check = mocker.Mock(spec=Check)
    round = random.randint(0, 100)
    with pytest.raises(KeyError):
        measurer.measurement_target(check, round)


def test_measurer_measurement_target_succeeds_otherwise(mocker: MockerFixture):
    measurer = Measurer()
    check = mocker.Mock(spec=Check)
    round = random.randint(0, 100)

    measurement_number = random.randint(0, 100)
    measurer.measurement_numbers[(check, round)] = measurement_number

    total_measurements = random.randint(measurement_number + 1, 100)
    measurer.total_measurements = total_measurements

    target = measurer.measurement_target(check, round)
    expected = stim.target_rec(measurement_number - total_measurements)
    assert target == expected


def test_measurer_can_compile_detector_false_if_not_all_measured(mocker: MockerFixture):
    measurer = Measurer()
    detector = mocker.Mock(spec=Detector)
    num_final_checks = random.randint(1, 10)
    detector.final_checks = [
        mocker.Mock(spec=Check) for _ in range(num_final_checks)]
    measurer.detectors_compiled = {}

    round = random.randint(0, 100)
    can_compile = measurer.can_compile_detector(detector, round)
    assert not can_compile


def test_measurer_can_compile_detector_false_if_already_compiled(mocker: MockerFixture):
    # Explicit test
    measurer = Measurer()
    round = 0
    num_checks = 3
    checks = [mocker.Mock(spec=Check) for _ in range(num_checks)]

    # First make it look like these checks have already been measured
    # in this round
    for i, check in enumerate(checks):
        measurer.measurement_numbers[(check, round)] = i
    # Now make it look like a detector consisting of these checks has
    # already been compiled.
    measurer.detectors_compiled[tuple(range(num_checks))] = True

    # Next, make a detector with these checks
    detector = mocker.Mock(spec=Detector)
    detector.final_checks = checks
    detector.timed_checks_mod_2 = [(0, check) for check in checks]

    can_compile = measurer.can_compile_detector(detector, round)
    assert not can_compile


def test_measurer_can_compile_detector_true_otherwise(mocker: MockerFixture):
    # Explicit test
    measurer = Measurer()
    round = 0
    num_checks = 3
    checks = [mocker.Mock(spec=Check) for _ in range(num_checks)]

    # First make it look like these checks have already been measured
    # in this round
    for i, check in enumerate(checks):
        measurer.measurement_numbers[(check, round)] = i

    # Then make it look like no equivalent detector has been compiled.
    measurer.detectors_compiled = defaultdict(lambda: False)

    # Next, make a detector with these checks
    detector = mocker.Mock(spec=Detector)
    detector.final_checks = checks
    detector.timed_checks_mod_2 = [(0, check) for check in checks]

    round = 0
    can_compile = measurer.can_compile_detector(detector, round)
    assert can_compile


def test_measurer_detector_to_stim_when_tracking_tuple_coords(mocker: MockerFixture):
    measurer = Measurer()
    measurer.measurement_target = mocker.Mock(return_value=0)

    num_checks = 3
    checks = [mocker.Mock(spec=Check) for _ in range(num_checks)]
    detector = mocker.Mock(spec=Detector)
    detector.timed_checks_mod_2 = [(0, check) for check in checks]
    detector.anchor = (0,)

    instruction = measurer.detector_to_stim(detector, round=0, track_coords=True)
    expected_targets = [0 for _ in range(num_checks)]
    expected_anchor = (0,)
    expected = stim.CircuitInstruction(
        'DETECTOR', expected_targets, expected_anchor)
    assert instruction == expected


def test_measurer_detector_to_stim_when_tracking_non_tuple_coords(mocker: MockerFixture):
    measurer = Measurer()
    measurer.measurement_target = mocker.Mock(return_value=0)

    num_checks = 3
    checks = [mocker.Mock(spec=Check) for _ in range(num_checks)]
    detector = mocker.Mock(spec=Detector)
    detector.timed_checks_mod_2 = [(0, check) for check in checks]
    detector.anchor = 0

    instruction = measurer.detector_to_stim(detector, round=0, track_coords=True)
    expected_targets = [0 for _ in range(num_checks)]
    expected_anchor = (0,)
    expected = stim.CircuitInstruction(
        'DETECTOR', expected_targets, expected_anchor)
    assert instruction == expected


def test_measurer_detector_to_stim_when_not_tracking_coords(mocker: MockerFixture):
    measurer = Measurer()
    measurer.measurement_target = mocker.Mock(return_value=0)

    num_checks = 3
    checks = [mocker.Mock(spec=Check) for _ in range(num_checks)]
    detector = mocker.Mock(spec=Detector)
    detector.timed_checks_mod_2 = [(0, check) for check in checks]

    instruction = measurer.detector_to_stim(detector, round=0, track_coords=False)
    expected_targets = [0 for _ in range(num_checks)]
    expected_anchor = ()
    expected = stim.CircuitInstruction(
        'DETECTOR', expected_targets, expected_anchor)
    assert instruction == expected


def test_measurer_measurement_triggers_to_stim_compiles_detector(mocker: MockerFixture):
    # Create measurement instructions that tell us checks' measurement outcomes
    num_measurements = 2
    round = 0
    measurements = [
        mocker.Mock(spec=Instruction) for _ in range(num_measurements)]
    checks = [mocker.Mock(spec=Check) for _ in range(num_measurements)]

    # Create a detector that consists of these checks
    detector = mocker.Mock(spec=Detector)
    detector.final_checks = checks
    detector.timed_checks_mod_2 = [(round, check) for check in checks]

    # Create a measurer class that knows about these measurements, checks
    # and detector
    measurer = Measurer()
    measurer.measurement_checks = {
        measurement: (check, round)
        for measurement, check in zip(measurements, checks)}
    measurer.triggers = {
        (check, round): [detector]
        for check in checks}

    # Get the instructions triggered by these measurements
    triggered = measurer.measurement_triggers_to_stim(measurements, None)

    # Assert that the expected detector is compiled.
    expected_targets = [
        stim.target_rec(-i) for i in range(num_measurements, 0, -1)]
    expected_detector_instruction = stim.CircuitInstruction(
        "DETECTOR", expected_targets, ())
    assert triggered == [expected_detector_instruction]
    assert measurer.total_measurements == num_measurements


def test_measurer_measurement_triggers_to_stim_compiles_observable(mocker: MockerFixture):
    # Create measurement instructions that tell us checks' measurement outcomes
    num_measurements = 2
    round = 0
    measurements = [
        mocker.Mock(spec=Instruction) for _ in range(num_measurements)]
    checks = [mocker.Mock(spec=Check) for _ in range(num_measurements)]

    # Create an observable that these checks will be multiplied into
    observable = mocker.Mock(spec=LogicalOperator)

    # Create a measurer class that knows about these measurements, checks
    # and observable
    measurer = Measurer()
    measurer.measurement_checks = {
        measurement: (check, round)
        for measurement, check in zip(measurements, checks)}
    measurer.triggers = {
        (check, round): [observable]
        for check in checks}

    # Get the instructions triggered by these measurements
    triggered = measurer.measurement_triggers_to_stim(measurements, None)

    # Assert that the expected observable instructions are compiled.
    expected_targets = [
        stim.target_rec(-i) for i in range(num_measurements, 0, -1)]
    expected_observable_instruction = stim.CircuitInstruction(
        "OBSERVABLE_INCLUDE", expected_targets, [0])
    assert triggered == [expected_observable_instruction]
    assert measurer.total_measurements == num_measurements

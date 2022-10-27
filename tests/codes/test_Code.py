import pytest
from _pytest.monkeypatch import MonkeyPatch
from pytest_mock import MockerFixture

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.Code import Code


def test_code_fails_if_no_data_qubits():
    expected_error = "Can't make a code without any data qubits"
    with pytest.raises(ValueError, match=expected_error):
        Code([])
    with pytest.raises(ValueError, match=expected_error):
        Code({})


def test_code_set_schedule_called_in_init_if_code_schedule_given(
        mocker: MockerFixture, monkeypatch: MonkeyPatch):
    data_qubits = [Qubit(i) for i in range(10)]
    checks = [mocker.Mock(spec=Check) for _ in range(3)]
    check_schedule = [checks]
    mock_set_schedule = mocker.Mock()
    monkeypatch.setattr(Code, 'set_schedules', mock_set_schedule)

    Code(data_qubits, check_schedule)
    mock_set_schedule.assert_called_with(check_schedule, None)


def test_code_set_schedule_not_called_in_init_if_code_schedule_not_given(
        mocker: MockerFixture, monkeypatch: MonkeyPatch):
    data_qubits = [Qubit(i) for i in range(10)]
    mock_set_schedule = mocker.Mock()
    monkeypatch.setattr(Code, 'set_schedules', mock_set_schedule)

    Code(data_qubits)
    mock_set_schedule.assert_not_called()


def test_code_fails_if_data_qubit_dimensions_vary():
    expected_error = \
        "Data qubits in a code must all have the same dimensions"

    # Explicit example
    data_qubits = [Qubit(0), Qubit((1, 1))]
    with pytest.raises(ValueError, match=expected_error):
        Code(data_qubits)


def test_code_fails_if_data_qubit_types_vary():
    expected_error = \
        "Data qubits in a code must either all have tuple coordinates " \
        "or all have non-tuple coordinates"

    # Explicit example
    data_qubits = [Qubit(0), Qubit((1,))]
    with pytest.raises(ValueError, match=expected_error):
        Code(data_qubits)


def test_code_fails_if_data_qubit_coordinates_non_unique():
    expected_error = \
        "Data qubits in a code must all have unique coordinates"

    # Explicit example
    data_qubits = [Qubit(0), Qubit((0))]
    with pytest.raises(ValueError, match=expected_error):
        Code(data_qubits)


def test_code_dimension_correct_otherwise():
    # Explicit test
    data_qubits = [Qubit(i) for i in range(10)]
    code = Code(data_qubits)
    assert code.dimension == 1

    data_qubits = [Qubit((i, i)) for i in range(10)]
    code = Code(data_qubits)
    assert code.dimension == 2


def test_code_set_schedules_fails_if_schedule_empty():
    expected_error = "Check schedule must have at least one round"
    data_qubits = [Qubit(i) for i in range(3)]
    code = Code(data_qubits)
    with pytest.raises(ValueError, match=expected_error):
        code.set_schedules([])


def test_code_set_schedules_fails_if_check_contains_unknown_data_qubit():
    expected_error = \
        "Checks within a code should only involve that code's data qubits"
    qubits = [Qubit(0), Qubit(1)]
    data_qubits = [qubits[0]]
    check = Check([Pauli(qubits[1], PauliLetter('X'))])
    code = Code(data_qubits)
    with pytest.raises(ValueError, match=expected_error):
        code.set_schedules([[check]])


def test_code_set_schedules_fails_if_check_schedule_length_greater_than_one_and_no_detector_schedule_given(
        mocker: MockerFixture, monkeypatch: MonkeyPatch):
    expected_error = \
        "Can't auto-create a detector schedule for a check schedule with " \
        "more than one round"
    # Patch over the validation on the data qubits and checks.
    monkeypatch.setattr(
        Code, '_assert_data_qubits_valid', mocker.Mock(return_value=True))
    monkeypatch.setattr(
        Code, '_assert_check_schedule_valid', mocker.Mock(return_value=True))

    checks = [mocker.Mock(spec=Check) for _ in range(3)]
    # Create a check schedule with two rounds.
    check_schedule = [checks, checks]

    code = Code([])
    with pytest.raises(ValueError, match=expected_error):
        code.set_schedules(check_schedule)


def test_code_set_schedules_detectors_auto_created_when_expected(
        mocker: MockerFixture, monkeypatch: MonkeyPatch):
    # Patch over the validation on the data qubits and checks.
    monkeypatch.setattr(
        Code, '_assert_data_qubits_valid', mocker.Mock(return_value=True))
    monkeypatch.setattr(
        Code, '_assert_check_schedule_valid', mocker.Mock(return_value=True))

    checks = [mocker.Mock(spec=Code) for _ in range(3)]
    for check in checks:
        check.anchor = None
    # Create a check schedule with just one round.
    check_schedule = [checks]

    # Mock up a Drum constructor so we can check it gets called correctly.
    mock_drum_init = mocker.Mock(return_value=None)
    monkeypatch.setattr('main.codes.Code.Drum', mock_drum_init)

    code = Code([])
    code.set_schedules(check_schedule, None)

    expected_calls = [
        mocker.call([(-1, check)], [(0, check)], 0, check.anchor)
        for check in checks]
    mock_drum_init.assert_has_calls(expected_calls)

    assert code.detector_schedule == [[None for _ in checks]]


def test_code_set_schedules_fails_if_schedule_lengths_differ(
        mocker: MockerFixture, monkeypatch: MonkeyPatch):
    expected_error = \
        "Detector schedule length must be the same as the check " \
        "schedule length"
    monkeypatch.setattr(
        Code, '_assert_data_qubits_valid', mocker.Mock(return_value=True))
    monkeypatch.setattr(
        Code, '_assert_check_schedule_valid', mocker.Mock(return_value=True))

    checks = [mocker.Mock(spec=Code) for _ in range(3)]
    # Create a check schedule with just one round...
    check_schedule = [checks]
    detectors = [mocker.Mock(spec=Code) for _ in range(3)]
    # ... but a detector schedule with multiple rounds.
    detector_schedule = [detectors, detectors]

    code = Code([])
    with pytest.raises(ValueError, match=expected_error):
        code.set_schedules(check_schedule, detector_schedule)


def test_code_set_schedules_fails_if_detector_contains_unknown_check(
        mocker: MockerFixture, monkeypatch: MonkeyPatch):
    expected_error = \
        "Detectors within a code should only involve checks in the code's " \
        "check schedule"
    monkeypatch.setattr(
        Code, '_assert_data_qubits_valid', mocker.Mock(return_value=True))
    monkeypatch.setattr(
        Code, '_assert_check_schedule_valid', mocker.Mock(return_value=True))

    checks = [mocker.Mock(spec=Code) for _ in range(3)]
    # Create a check schedule with just one round
    check_schedule = [checks]

    detectors = [mocker.Mock(spec=Code) for _ in range(3)]
    # Add an unknown check to one of the detectors
    detectors[0].timed_checks = [(0, mocker.Mock(spec=Check))]
    for detector in detectors[1:]:
        detector.timed_checks = []
    detector_schedule = [detectors]

    code = Code([])
    with pytest.raises(ValueError, match=expected_error):
        code.set_schedules(check_schedule, detector_schedule)


def test_code_attributes_all_initialised(mocker: MockerFixture, monkeypatch: MonkeyPatch):
    # Assume all validations pass
    monkeypatch.setattr(
        Code, '_assert_data_qubits_valid', mocker.Mock(return_value=True))
    monkeypatch.setattr(
        Code, '_assert_check_schedule_valid', mocker.Mock(return_value=True))
    monkeypatch.setattr(
        Code, '_assert_detector_schedule_valid', mocker.Mock(return_value=True))

    data_qubits = [mocker.Mock(spec=Qubit) for _ in range(3)]
    checks = [mocker.Mock(spec=Check) for _ in range(3)]
    detectors = [mocker.Mock(spec=Drum) for _ in range(3)]

    schedule_length = 2
    check_schedule = [checks for _ in range(schedule_length)]
    detector_schedule = [detectors for _ in range(schedule_length)]

    logical_qubits = [mocker.Mock(spec=LogicalQubit)]
    distance = 5

    code = Code(
        data_qubits,
        check_schedule,
        detector_schedule,
        logical_qubits,
        distance)

    assert code.data_qubits == {
        # Should be converted to a dictionary
        i: qubit for i, qubit in enumerate(data_qubits)}
    assert code.check_schedule == check_schedule
    assert code.detector_schedule == detector_schedule
    assert code.schedule_length == schedule_length
    assert code.logical_qubits == logical_qubits
    assert code.distance == code.distance
    assert code.checks == set(checks)
    assert code.detectors == set(detectors)
    assert code.ancilla_qubits == {}


# TODO - would be nice to add a test here to check that a logical operator
#  only ever involves data qubits that are actually part of the code. But
#  because logical operators may be dynamic, their Paulis are generated on
#  the fly each round.

import random
from functools import reduce
from operator import mul

import stim
from _pytest.monkeypatch import MonkeyPatch
from pytest_mock import MockerFixture

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.detectors.Detector import Detector
from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.codes.Code import Code
from main.compiling.Circuit import Circuit
from main.compiling.Instruction import Instruction
from main.compiling.compilers.Compiler import Compiler
from main.compiling.compilers.DetectorInitialiser import DetectorInitialiser
from tests.building_blocks.pauli.utils_paulis import random_paulis
from tests.building_blocks.utils_checks import random_check, specific_check
from tests.compiling.utils_instructions import MockInstruction
from tests.utils.utils_numbers import default_test_repeats_medium, default_max_unique_sample_size


def test_detector_initialiser_to_pauli_string():
    # Explicit test:
    qubits = [Qubit(i) for i in range(4)]
    product = PauliProduct([
        Pauli(qubits[0], PauliLetter('X')),
        Pauli(qubits[1], PauliLetter('Y')),
        Pauli(qubits[2], PauliLetter('Z')),
        Pauli(qubits[3], PauliLetter('I'))])
    circuit = Circuit()
    circuit.qubits = set(qubits)
    circuit._qubit_indexes = {qubit: qubit.coords for qubit in qubits}
    string = DetectorInitialiser.to_pauli_string(product, circuit)
    assert string == stim.PauliString('+XYZ_')

    # Random tests:
    stim_signs = {
        1: '+',
        1j: '+i',
        -1: '-',
        -1j: '-i'}
    for _ in range(default_test_repeats_medium):
        dimension = random.randint(1, 10)
        max_paulis = random.randint(0, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(dimension))
        paulis = random_paulis(
            num_paulis, unique_qubits=True, dimension=dimension, int_coords=True)
        product = PauliProduct(paulis)

        qubits = [pauli.qubit for pauli in paulis]
        circuit = Circuit()
        circuit.qubits = set(qubits)
        circuit._qubit_indexes = {qubit: i for i, qubit in enumerate(qubits)}

        letters = ''.join(pauli.letter.letter for pauli in paulis)
        sign = reduce(mul, [pauli.letter.sign for pauli in paulis], 1)
        stim_sign = stim_signs[sign]
        expected = stim.PauliString(stim_sign + letters)

        string = DetectorInitialiser.to_pauli_string(product, circuit)
        assert string == expected


def test_detector_initialiser_is_deterministic(mocker: MockerFixture):
    # Probably only going to be able to manage an explicit test here.

    # Initialise two qubits in the zero state
    circuit = Circuit()
    qubits = [Qubit(0), Qubit(1)]
    for qubit in qubits:
        circuit.initialise(0, Instruction([qubit], 'RZ'))

    # Create corresponding simulator
    simulator = stim.TableauSimulator()
    simulator.do(stim.Circuit("RZ 0 1"))

    # Create initialiser
    code = mocker.Mock(spec=Code)
    compiler = mocker.Mock(spec=Compiler)
    initialiser = DetectorInitialiser(code, compiler)

    # Consider two single qubit Z checks
    timed_checks = [
        (0, Check([Pauli(qubits[0], PauliLetter('Z'))])),
        (0, Check([Pauli(qubits[1], PauliLetter('Z'))]))]

    is_deterministic = initialiser.is_deterministic(
        timed_checks, circuit, simulator)
    assert is_deterministic

    # Now consider two single qubit X checks
    timed_checks = [
        (0, Check([Pauli(qubits[0], PauliLetter('X'))])),
        (0, Check([Pauli(qubits[1], PauliLetter('X'))]))]

    is_deterministic = initialiser.is_deterministic(
        timed_checks, circuit, simulator)
    assert not is_deterministic


def test_detector_initialiser_product_measurement_targets(mocker: MockerFixture):
    # Explicit test: create an XYZ check
    qubits = [Qubit(i) for i in range(3)]
    check = Check([
        Pauli(qubits[0], PauliLetter('X')),
        Pauli(qubits[1], PauliLetter('Y')),
        Pauli(qubits[2], PauliLetter('Z'))])

    # Create circuit
    circuit = Circuit()
    circuit.qubits = set(qubits)
    circuit._qubit_indexes = {qubit: qubit.coords for qubit in qubits}

    targets = circuit.product_measurement_targets(check)
    expected = [
        stim.target_x(0),
        stim.target_combiner(),
        stim.target_y(1),
        stim.target_combiner(),
        stim.target_z(2)]
    assert targets == expected

    # Random tests
    targeters = {
        'X': stim.target_x,
        'Y': stim.target_y,
        'Z': stim.target_z}
    for _ in range(default_test_repeats_medium):
        # Create a check
        weight = random.randint(1, 10)
        dimension = random.randint(1, 10)
        check = random_check(weight, dimension, int_coords=True)

        # Create circuit
        circuit = Circuit()
        # Only care about non-identity Paulis
        paulis = [
            pauli for pauli in check.paulis.values()
            if pauli.letter.letter != 'I']
        qubits = [pauli.qubit for pauli in paulis]
        circuit.qubits = set(qubits)
        circuit._qubit_indexes = {qubit: i for i, qubit in enumerate(qubits)}

        targets = circuit.product_measurement_targets(check)

        expected = [stim.target_combiner() for _ in range(2 * len(paulis) - 1)]
        invert = check.product.word.sign == -1
        expected[0] = targeters[paulis[0].letter.letter](0, invert)
        for i in range(1, len(paulis)):
            expected[2*i] = targeters[paulis[i].letter.letter](i)

        assert targets == expected


def test_detector_initialiser_measure_checks(mocker: MockerFixture):
    # Explicit test
    code = mocker.Mock(spec=Code)
    compiler = mocker.Mock(spec=Compiler)
    detector_initialiser = DetectorInitialiser(code, compiler)

    qubits = [Qubit(i) for i in range(3)]
    check_0 = Check([
        Pauli(qubits[0], PauliLetter('X')),
        Pauli(qubits[1], PauliLetter('Y'))])
    check_1 = Check([
        Pauli(qubits[1], PauliLetter('Y')),
        Pauli(qubits[2], PauliLetter('Z'))])
    code.schedule_length = 2
    code.check_schedule = [[check_0], [check_1]]

    circuit = Circuit()
    circuit.product_measurement_targets = \
        mocker.Mock(return_value=None)
    circuit.measure = mocker.Mock()

    # Measure round 0 check
    detector_initialiser.measure_checks(0, 0, circuit)
    expected_measurement = MockInstruction(
        qubits[:2], 'MPP', is_measurement=True)
    circuit.measure.assert_called_with(expected_measurement, check_0, 0, 0)

    # Measure round 1 check
    detector_initialiser.measure_checks(1, 2, circuit)
    expected_measurement = MockInstruction(
        qubits[1:], 'MPP', is_measurement=True)
    circuit.measure.assert_called_with(expected_measurement, check_1, 1, 2)


def test_detector_initialiser_get_round_detectors_given_deterministic_lid_only_detector(mocker: MockerFixture):
    # Explicit test
    code = mocker.Mock(spec=Code)
    compiler = mocker.Mock(spec=Compiler)
    detector_initialiser = DetectorInitialiser(code, compiler)

    check = specific_check(['X', 'X'])
    drum = Drum(floor=[(-2, check)], lid=[(0, check)], end=1)

    code.schedule_length = 2
    code.detector_schedule = [[], [drum]]

    detector_initialiser.is_deterministic = mocker.Mock(return_value=True)

    circuit = mocker.Mock(spec=Circuit)
    simulator = mocker.Mock(spec=stim.TableauSimulator)
    detectors = detector_initialiser.get_round_detectors(1, circuit, simulator)

    assert len(detectors) == 1
    detector = detectors[0]
    assert isinstance(detector, Stabilizer)
    assert detector.timed_checks == [(0, check)]
    assert detector.end == 1
    assert detector.anchor == drum.anchor


def test_detector_initialiser_get_round_detectors_given_non_deterministic_lid_only_detector(mocker: MockerFixture):
    # Explicit test
    code = mocker.Mock(spec=Code)
    compiler = mocker.Mock(spec=Compiler)
    detector_initialiser = DetectorInitialiser(code, compiler)

    check = specific_check(['X', 'X'])
    drum = Drum(floor=[(-2, check)], lid=[(0, check)], end=1)

    code.schedule_length = 2
    code.detector_schedule = [[], [drum]]

    detector_initialiser.is_deterministic = mocker.Mock(return_value=False)

    circuit = mocker.Mock(spec=Circuit)
    simulator = mocker.Mock(spec=stim.TableauSimulator)
    detectors = detector_initialiser.get_round_detectors(1, circuit, simulator)

    assert detectors == []


def test_detector_initialiser_get_round_detectors_given_untruncated_detector(mocker: MockerFixture):
    # Explicit test
    code = mocker.Mock(spec=Code)
    compiler = mocker.Mock(spec=Compiler)
    detector_initialiser = DetectorInitialiser(code, compiler)

    check = specific_check(['X', 'X'])
    drum = Drum(floor=[(-2, check)], lid=[(0, check)], end=0)

    code.schedule_length = 2
    code.detector_schedule = [[drum], []]

    detector_initialiser.is_deterministic = mocker.Mock(return_value=True)

    circuit = mocker.Mock(spec=Circuit)
    simulator = mocker.Mock(spec=stim.TableauSimulator)
    detectors = detector_initialiser.get_round_detectors(2, circuit, simulator)

    assert detectors == [drum]


def test_detector_initialiser_set_initial_stabilizers_as_detectors(mocker: MockerFixture):
    # Explicit test
    code = mocker.Mock(spec=Code)
    compiler = mocker.Mock(spec=Compiler)
    initialiser = DetectorInitialiser(code, compiler)
    initialiser.measure_checks = mocker.Mock()

    # Mock up some initial stabilizers.
    num_rounds = 3
    initial_stabilizers = [mocker.Mock(Stabilizer) for _ in range(num_rounds)]
    for i, stabilizer in enumerate(initial_stabilizers):
        # Suppose the last check in this stabilizer is measured in round i.
        stabilizer.end = i

    circuit = Circuit()
    tick = 0
    next_tick, initial_detector_schedule = initialiser.use_stabilizers_as_detectors(
        initial_stabilizers, tick, circuit)

    expected_detector_schedule = {
        i: [stabilizer] for i, stabilizer in enumerate(initial_stabilizers)}
    assert initial_detector_schedule == expected_detector_schedule
    expected_calls = [
        mocker.call(i, 2*i, circuit) for i in range(num_rounds)]
    initialiser.measure_checks.assert_has_calls(expected_calls)
    assert next_tick == 2 * num_rounds


def test_detector_initialiser_simulate_round(mocker: MockerFixture, monkeypatch: MonkeyPatch):
    code = mocker.Mock(spec=Code)
    compiler = mocker.Mock(spec=Compiler)
    initialiser = DetectorInitialiser(code, compiler)

    initialiser.measure_checks = mocker.Mock()
    initialiser.get_round_detectors = mocker.Mock()

    circuit = mocker.Mock(spec=Circuit)
    circuit.to_stim = mocker.Mock()
    simulator = mocker.Mock(spec=stim.TableauSimulator)
    monkeypatch.setattr(
        stim, 'TableauSimulator', mocker.Mock(return_value=simulator))
    simulator.do = mocker.Mock()

    initialiser.simulate_round(0, 0, circuit)

    initialiser.get_round_detectors.assert_called_with(0, circuit, simulator)
    initialiser.measure_checks.assert_called_with(0, 0, circuit)


def test_detector_initialiser_split_schedule(mocker: MockerFixture):
    code = mocker.Mock(spec=Code)
    compiler = mocker.Mock(spec=Compiler)
    initialiser = DetectorInitialiser(code, compiler)

    code.schedule_length = 2
    code.detector_schedule = [
        [mocker.Mock(spec=Detector)] for _ in range(code.schedule_length)]
    num_rounds = 3
    initial_detectors = [
        [mocker.Mock(spec=Detector)] for _ in range(num_rounds)]
    initial_detector_schedule = {
        i: detectors for i, detectors in enumerate(initial_detectors)}

    result = initialiser.split_schedule(initial_detector_schedule)
    expected = \
        [initial_detectors[:2]] + \
        [initial_detectors[2:3] + code.detector_schedule[1:]]
    assert result == expected


def test_detector_initialiser_get_initial_detectors_without_initial_stabilizers(mocker: MockerFixture):
    code = mocker.Mock(spec=Code)
    compiler = mocker.Mock(spec=Compiler)
    initialiser = DetectorInitialiser(code, compiler)

    # Put a single detector in each round of the schedule
    code.schedule_length = 2
    # Assume every detector spans three rounds. Then we should be done with
    # special initial detector logic after two rounds.
    detector_span = 3
    code.detector_schedule = [
        [mocker.Mock(spec=Drum)] for _ in range(code.schedule_length)]
    code.detectors = [drums[0] for drums in code.detector_schedule]
    for i, drums in enumerate(code.detector_schedule):
        drums[0].end = i
        drums[0].floor_start = i - detector_span

    # Set up data for mocking over inner methods.
    initial_detectors = [
        [mocker.Mock(spec=Stabilizer)] for _ in range(detector_span)]

    def mock_simulate_round(round, tick, circuit):
        return initial_detectors[round]

    # Mock over the inner methods.
    circuit = Circuit()
    initialiser.simulate_round = mocker.Mock(side_effect=mock_simulate_round)
    initialiser.initialise_circuit = mocker.Mock(return_value=(0, circuit))
    initialiser.split_schedule = mocker.Mock()

    # Call the main method.
    initialiser.get_initial_detectors(
        initial_states={},
        initial_stabilizers=None)

    # Let's say the method worked if the expected thing was passed to
    # the split_schedule method.
    expected = {
        i: detectors for i, detectors in enumerate(initial_detectors)}
    initialiser.split_schedule.assert_called_with(expected)


def test_detector_initialiser_get_initial_detectors_given_initial_stabilizers(mocker: MockerFixture):
    code = mocker.Mock(spec=Code)
    compiler = mocker.Mock(spec=Compiler)
    initialiser = DetectorInitialiser(code, compiler)

    # Supply one round of initial stabilizers,
    # with just one stabilizer in this round.
    num_rounds_initial_stabilizers = 1
    initial_stabilizers_schedule = {}
    initial_stabilizers = [
        mocker.Mock(spec=Stabilizer)
        for _ in range(num_rounds_initial_stabilizers)]
    for i, stabilizer in enumerate(initial_stabilizers):
        stabilizer.end = i
        initial_stabilizers_schedule[i] = [stabilizer]

    # Put a single detector in each round of the schedule
    code.schedule_length = 2
    # Assume every detector spans three rounds. Then we should be done with
    # special initial detector logic after two rounds.
    detector_span = 3
    code.detector_schedule = [
        [mocker.Mock(spec=Drum)] for _ in range(code.schedule_length)]
    code.detectors = [drums[0] for drums in code.detector_schedule]
    for i, drums in enumerate(code.detector_schedule):
        drums[0].end = i
        drums[0].floor_start = i - detector_span

    # Set up data for mocking over inner methods.
    initial_detectors = [
        [mocker.Mock(spec=Stabilizer)] for _ in range(detector_span)]

    def mock_simulate_round(round, tick, circuit):
        return initial_detectors[round]

    # Mock over the inner methods.
    circuit = Circuit()
    initialiser.simulate_round = mocker.Mock(side_effect=mock_simulate_round)
    initialiser.initialise_circuit = mocker.Mock(return_value=(0, circuit))
    initialiser.split_schedule = mocker.Mock()
    initialiser.use_stabilizers_as_detectors = mocker.Mock(
        return_value=(2, initial_stabilizers_schedule))

    # Call the main method.
    initialiser.get_initial_detectors(
        initial_states={},
        initial_stabilizers=initial_stabilizers)

    # Let's say the method worked if the expected thing was passed to
    # the split_schedule method.
    expected_initial_detectors = \
        [initial_stabilizers] + \
        initial_detectors[num_rounds_initial_stabilizers:]
    expected = {
        i: detectors
        for i, detectors in enumerate(expected_initial_detectors)}
    initialiser.split_schedule.assert_called_with(expected)

import random

import stim
import pytest
from _pytest.monkeypatch import MonkeyPatch
from pytest_mock import MockerFixture

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.detectors.Detector import Detector
from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.Code import Code
from main.compiling.Circuit import Circuit
from main.compiling.Instruction import Instruction
from main.compiling.Measurer import Measurer
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.codes.RepetitionCode import RepetitionCode
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.compiling.compilers.Compiler import Compiler
from main.compiling.compilers.DetectorInitialiser import DetectorInitialiser
from main.compiling.noise.models import CircuitLevelNoise, CodeCapacityBitFlipNoise, PhenomenologicalNoise
from main.compiling.noise.models.NoNoise import NoNoise
from main.compiling.syndrome_extraction.controlled_gate_orderers.RotatedSurfaceCodeOrderer import \
    RotatedSurfaceCodeOrderer
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import TrivialOrderer
from main.compiling.syndrome_extraction.extractors import SyndromeExtractor
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CnotExtractor import CnotExtractor
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
from main.utils.enums import State
from tests.compiling.utils_instructions import MockInstruction
from tests.utils.utils_numbers import default_test_repeats_small

test_qpu = SquareLatticeQPU((3, 1))
rep_code = RepetitionCode(2)
test_qpu.embed(rep_code, (0, 0), 0)
trivial_orderer = TrivialOrderer()
extractor = CxCyCzExtractor(trivial_orderer)
noise_model = CircuitLevelNoise(0.1, 0.15, 0.05, 0.03, 0.03)
test_compiler = AncillaPerCheckCompiler(noise_model, extractor)
rep_qubits = list(rep_code.data_qubits.values())
rep_initials_zero = {qubit: State.Zero for qubit in rep_qubits}
rep_initials_plus = {qubit: State.Plus for qubit in rep_qubits}
rep_finals = [Pauli(qubit, PauliLetter('Z')) for qubit in rep_qubits]
rep_logicals = [rep_code.logical_qubits[0].z]


# TESTS
# - X test init and defaults
# - X test fails if initialisation instructions don't start with R_
# - X test fails if measurement instructions don't end with M_
# - X get_measurement_bases
# - X get_initial_states
# - X compile_initialisation
# - X initialize_qubits
# - compile_layer
# - X compile_round
# - X add_start_of_round_noise
# - X compile_final_measurements
# - X compile_final_detectors
# - X compile_final_detectors_from_stabilizers
# - X compile_final_detectors_from_measurements
# - X compile_final_logical_operators
# - X measure_qubits
# - X compile_gates
# - X - fails if gate size not 1 or 2
# - X - handles noise correctly
# - compile_to_circuit
# - compile_to_stim


def test_compiler_fails_if_initialisation_instructions_invalid(
        monkeypatch: MonkeyPatch):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    expected_error = \
        "All initialisation instructions should start with a reset gate"
    initialisation_instructions = {
        State.Zero: ['Not a reset gate', 'Some other gate']}
    with pytest.raises(ValueError, match=expected_error):
        Compiler(initialisation_instructions=initialisation_instructions)


def test_compiler_fails_if_measurement_instructions_invalid(
        monkeypatch: MonkeyPatch):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    expected_error = \
        "All measurement instructions should end with a measurement gate"
    measurement_instructions = {
        PauliLetter('X'): ['Some gate', 'Not a measurement gate']}
    with pytest.raises(ValueError, match=expected_error):
        Compiler(measurement_instructions=measurement_instructions)


def test_compiler_init_has_correct_defaults(
        monkeypatch: MonkeyPatch):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    assert compiler.noise_model == NoNoise()
    assert compiler.syndrome_extractor == CnotExtractor()
    assert compiler.initialisation_instructions == {
        State.Zero: ["RZ"],
        State.One: ["RZ", "X"],
        State.Plus: ["RX"],
        State.Minus: ["RX", "Z"],
        State.I: ["RY"],
        State.MinusI: ["RY", "X"]}
    assert compiler.measurement_instructions == {
        PauliLetter('X'): ["MX"],
        PauliLetter('Y'): ["MY"],
        PauliLetter('Z'): ["MZ"]}


def test_compiler_get_measurement_bases_and_initial_states_fails_if_stabilizers_inconsistent(
        mocker: MockerFixture, monkeypatch: MonkeyPatch):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    expected_error = "The desired stabilizers are inconsistent"
    compiler = Compiler()
    qubit = Qubit(0)
    stabilizers = [
        Stabilizer([(0, Check([Pauli(qubit, PauliLetter('X'))]))], 0),
        Stabilizer([(0, Check([Pauli(qubit, PauliLetter('Z'))]))], 0)]
    with pytest.raises(ValueError, match=expected_error):
        compiler.get_measurement_bases(stabilizers)
    with pytest.raises(ValueError, match=expected_error):
        compiler.get_initial_states(stabilizers)


def test_compiler_get_measurement_bases_and_initial_states_returns_positive_signed_pauli(
        mocker: MockerFixture, monkeypatch: MonkeyPatch):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    qubit = Qubit(0)
    stabilizers = [
        Stabilizer([(0, Check([Pauli(qubit, PauliLetter('X', -1))]))], 0)]
    measurement_bases = compiler.get_measurement_bases(stabilizers)
    initial_states = compiler.get_initial_states(stabilizers)

    assert measurement_bases == [Pauli(qubit, PauliLetter('X'))]
    assert initial_states == {qubit: State.Plus}


def test_compiler_compile_initialisation_adds_ancilla_qubits(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    compiler.add_ancilla_qubits = mocker.Mock()
    compiler.initialize_qubits = mocker.Mock()
    detector_initialiser = mocker.Mock(spec=DetectorInitialiser)
    monkeypatch.setattr(
        'main.compiling.compilers.Compiler.DetectorInitialiser',
        mocker.Mock(return_value=detector_initialiser))

    # Set up data to pass to method
    code = mocker.Mock(spec=Code)
    code.data_qubits = {}
    initial_states = {}
    initial_stabilizers = None
    compiler.compile_initialisation(code, initial_states, initial_stabilizers)

    compiler.add_ancilla_qubits.assert_called_with(code)


def test_compiler_compile_initialisation_gets_initial_states_if_stabilizers_given(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    compiler.add_ancilla_qubits = mocker.Mock()
    compiler.initialize_qubits = mocker.Mock()
    detector_initialiser = mocker.Mock(spec=DetectorInitialiser)
    monkeypatch.setattr(
        'main.compiling.compilers.Compiler.DetectorInitialiser',
        mocker.Mock(return_value=detector_initialiser))

    # Pass 'None' as initial states: instead use a list of stabilizers
    code = mocker.Mock(spec=Code)
    code.data_qubits = {}
    initial_states = None
    initial_stabilizers = []
    # Want get_initial_states to return an empty dictionary,
    # to match the code's data qubits
    compiler.get_initial_states = mocker.Mock(return_value={})
    compiler.compile_initialisation(code, initial_states, initial_stabilizers)

    compiler.get_initial_states.assert_called_with(initial_stabilizers)


def test_compiler_compile_initialisation_raises_error_if_initial_states_wrong(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    compiler.add_ancilla_qubits = mocker.Mock()
    compiler.initialize_qubits = mocker.Mock()
    detector_initialiser = mocker.Mock(spec=DetectorInitialiser)
    monkeypatch.setattr(
        'main.compiling.compilers.Compiler.DetectorInitialiser',
        mocker.Mock(return_value=detector_initialiser))

    code = mocker.Mock(spec=Code)
    # Make initial states different to code's data qubits
    code.data_qubits = {0: Qubit(0)}
    initial_states = {}
    initial_stabilizers = None

    expected_error = \
        "Set of data qubits whose initial states were either given or " \
        "could be determined differs from the set of all data qubits"
    with pytest.raises(ValueError, match=expected_error):
        compiler.compile_initialisation(
            code, initial_states, initial_stabilizers)


def test_compiler_compile_initialisation_initialises_qubits(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    compiler.add_ancilla_qubits = mocker.Mock()
    compiler.initialize_qubits = mocker.Mock()
    detector_initialiser = mocker.Mock(spec=DetectorInitialiser)
    circuit = mocker.Mock(spec=Circuit)
    monkeypatch.setattr(
        'main.compiling.compilers.Compiler.DetectorInitialiser',
        mocker.Mock(return_value=detector_initialiser))
    monkeypatch.setattr(
        'main.compiling.compilers.Compiler.Circuit',
        mocker.Mock(return_value=circuit))

    code = mocker.Mock(spec=Code)
    code.data_qubits = {}
    initial_states = {}
    initial_stabilizers = None
    compiler.compile_initialisation(code, initial_states, initial_stabilizers)

    compiler.initialize_qubits.assert_called_with(initial_states, 0, circuit)


def test_compiler_compile_initialisation_gets_initial_detectors(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    compiler.add_ancilla_qubits = mocker.Mock()
    compiler.initialize_qubits = mocker.Mock()
    detector_initialiser = mocker.Mock(spec=DetectorInitialiser)
    monkeypatch.setattr(
        'main.compiling.compilers.Compiler.DetectorInitialiser',
        mocker.Mock(return_value=detector_initialiser))

    # Set up data to pass to method
    code = mocker.Mock(spec=Code)
    code.data_qubits = {}
    initial_states = {}
    initial_stabilizers = None
    compiler.compile_initialisation(code, initial_states, initial_stabilizers)

    detector_initialiser.get_initial_detectors.assert_called_with(
        initial_states, initial_stabilizers)


def test_compiler_compile_initialisation_returns_correct_data(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    compiler.add_ancilla_qubits = mocker.Mock()

    # Set up mock return values from a few methods
    tick = 10
    compiler.initialize_qubits = mocker.Mock(return_value=tick)

    detector_initialiser = mocker.Mock(spec=DetectorInitialiser)
    initial_detector_schedules = [[], []]
    detector_initialiser.get_initial_detectors = mocker.Mock(
        return_value=initial_detector_schedules)
    monkeypatch.setattr(
        'main.compiling.compilers.Compiler.DetectorInitialiser',
        mocker.Mock(return_value=detector_initialiser))

    circuit = mocker.Mock(spec=Circuit)
    monkeypatch.setattr(
        'main.compiling.compilers.Compiler.Circuit',
        mocker.Mock(return_value=circuit))

    # Set up data to pass to method
    code = mocker.Mock(spec=Code)
    code.data_qubits = {}
    initial_states = {}
    initial_stabilizers = None

    result = compiler.compile_initialisation(
        code, initial_states, initial_stabilizers)
    expected = (initial_detector_schedules, tick, circuit)
    assert result == expected


def test_compiler_initialize_qubits_defaults_to_correct_initialisation_instructions(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    initialisation_instructions = {
        State.Zero: ['RZ'],
        State.Plus: ['RZ', 'H']}
    compiler = Compiler(initialisation_instructions=initialisation_instructions)
    compiler.compile_gates = mocker.Mock()

    # Explicit test
    qubits = [Qubit(0), Qubit(1)]
    initial_states = {
        qubits[0]: State.Zero,
        qubits[1]: State.Plus}
    tick = 0
    circuit = mocker.Mock(spec=Circuit)
    compiler.initialize_qubits(
        initial_states, tick, circuit, initialisation_instructions=None)

    # Assert correct instructions passed to circuit.
    circuit.initialise.has_calls([
        mocker.call(tick, MockInstruction(qubits[:1], 'RZ')),
        mocker.call(tick, MockInstruction(qubits[1:], 'RZ'))])
    compiler.compile_gates.assert_any_call(
        [MockInstruction(qubits[1:], 'H')], tick + 2, circuit)


def test_compiler_initialize_qubits_otherwise_uses_given_initialisation_instructions(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler_initialisation_instructions = {
        State.Zero: ['RZ'],
        State.Plus: ['RZ', 'H']}
    compiler = Compiler(
        initialisation_instructions=compiler_initialisation_instructions)
    compiler.compile_gates = mocker.Mock()

    # Explicit test
    qubits = [Qubit(0), Qubit(1)]
    initial_states = {
        qubits[0]: State.Zero,
        qubits[1]: State.Plus}
    tick = 0
    circuit = mocker.Mock(spec=Circuit)
    initialisation_instructions = {
        State.Zero: ['RX', 'H'],
        State.Plus: ['RX']}
    compiler.initialize_qubits(
        initial_states, tick, circuit, initialisation_instructions)

    # Assert correct instructions passed to circuit.
    circuit.initialise.has_calls([
        mocker.call(tick, MockInstruction(qubits[:1], 'RX')),
        mocker.call(tick, MockInstruction(qubits[1:], 'RX'))])
    compiler.compile_gates.assert_any_call(
        [MockInstruction(qubits[:1], 'H')], tick + 2, circuit)


def test_compiler_initialize_qubits_returns_correct_tick(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    # Explicit test
    qubits = [Qubit(0), Qubit(1)]
    initial_states = {
        qubits[0]: State.Zero,
        qubits[1]: State.Plus}
    tick = 0
    circuit = mocker.Mock(spec=Circuit)
    initialisation_instructions = {
        State.Zero: ['RZ', 'H', 'H'],
        State.Plus: ['RZ', 'H']}
    next_tick = compiler.initialize_qubits(
        initial_states, tick, circuit, initialisation_instructions)

    # Assert correct instructions passed to circuit.
    assert next_tick == tick + 6


def test_compiler_initialize_qubits_works_when_no_noise(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler(noise_model=NoNoise())

    # Explicit test
    qubits = [Qubit(0), Qubit(1)]
    initial_states = {
        qubits[0]: State.Zero,
        qubits[1]: State.Plus}
    tick = 0
    circuit = mocker.Mock(spec=Circuit)
    initialisation_instructions = {
        State.Zero: ['RZ'],
        State.Plus: ['RZ', 'H']}
    compiler.initialize_qubits(
        initial_states, tick, circuit, initialisation_instructions)

    # Assert no noise applied.
    assert all([
        call.args[1].name != 'PAULI_CHANNEL_1'
        for call in circuit.add_instruction.call_args_list])


def test_compiler_initialize_qubits_applies_noise_if_given(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    noise_model = CircuitLevelNoise(
        initialisation=0.1,
        one_qubit_gate=0.2)
    compiler = Compiler(noise_model=noise_model)

    # Explicit test
    qubits = [Qubit(0), Qubit(1)]
    initial_states = {
        qubits[0]: State.Zero,
        qubits[1]: State.Plus}
    tick = 0
    circuit = mocker.Mock(spec=Circuit)
    initialisation_instructions = {
        State.Zero: ['RZ'],
        State.Plus: ['RZ', 'H']}
    compiler.initialize_qubits(
        initial_states, tick, circuit, initialisation_instructions)

    # Assert correct noise applied.
    initialisation_noise = compiler.noise_model.initialisation
    one_qubit_gate_noise = compiler.noise_model.one_qubit_gate

    circuit.add_instruction.assert_any_call(tick + 1, MockInstruction(
        qubits[:1], initialisation_noise.name, initialisation_noise.params, is_noise=True))
    circuit.add_instruction.assert_any_call(tick + 1, MockInstruction(
        qubits[1:], initialisation_noise.name, initialisation_noise.params, is_noise=True))
    circuit.add_instruction.assert_any_call(tick + 3, MockInstruction(
        qubits[1:], one_qubit_gate_noise.name, one_qubit_gate_noise.params, is_noise=True))


def test_compiler_compile_round_adds_start_of_round_noise(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    # Mock over submethods used by this method
    compiler.add_start_of_round_noise = mocker.Mock()
    compiler.syndrome_extractor = mocker.Mock(spec=SyndromeExtractor)
    tick = 100
    compiler.syndrome_extractor.extract_checks = mocker.Mock(
        return_value=tick + 10)

    # Add some mock data, as well as mock methods on them
    circuit = mocker.Mock(spec=Circuit)
    circuit.measurer = mocker.Mock(spec=Measurer)
    circuit.measurer.add_detectors = mocker.Mock

    code = mocker.Mock(spec=Code)
    code.schedule_length = 5
    code.check_schedule = [
        [mocker.Mock(spec=Check)]
        for _ in range(code.schedule_length)]
    detector_schedule = [
        [mocker.Mock(spec=Detector)]
        for _ in range(code.schedule_length)]

    # ... set up even more data...
    round = 7
    relative_round = round % code.schedule_length
    observables = None

    # Call the method!
    compiler.compile_round(
        round, relative_round, detector_schedule, observables, tick, circuit, code)

    compiler.add_start_of_round_noise.assert_called_with(tick - 1, circuit, code)


def test_compiler_compile_round_calls_extract_checks_correctly(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    # Mock over submethods used by this method
    compiler.add_start_of_round_noise = mocker.Mock()
    compiler.syndrome_extractor = mocker.Mock(spec=SyndromeExtractor)
    tick = 100
    compiler.syndrome_extractor.extract_checks = mocker.Mock(
        return_value=tick + 10)

    # Add some mock data, as well as mock methods on them
    circuit = mocker.Mock(spec=Circuit)
    circuit.measurer = mocker.Mock(spec=Measurer)
    circuit.measurer.add_detectors = mocker.Mock

    code = mocker.Mock(spec=Code)
    code.schedule_length = 5
    code.check_schedule = [
        [mocker.Mock(spec=Check)]
        for _ in range(code.schedule_length)]
    detector_schedule = [
        [mocker.Mock(spec=Detector)]
        for _ in range(code.schedule_length)]

    # ... set up even more data...
    round = 7
    relative_round = round % code.schedule_length
    observables = None

    # Call the method!
    compiler.compile_round(
        round, relative_round, detector_schedule, observables, tick, circuit, code)

    compiler.syndrome_extractor.extract_checks.assert_called_with(
        code.check_schedule[relative_round], round, tick, circuit, compiler)


def test_compiler_compile_round_calls_add_detectors_correctly(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    # Mock over submethods used by this method
    compiler.add_start_of_round_noise = mocker.Mock()
    compiler.syndrome_extractor = mocker.Mock(spec=SyndromeExtractor)
    tick = 100
    compiler.syndrome_extractor.extract_checks = mocker.Mock(
        return_value=tick + 10)

    # Add some mock data, as well as mock methods on them
    circuit = mocker.Mock(spec=Circuit)
    circuit.measurer = mocker.Mock(spec=Measurer)
    circuit.measurer.add_detectors = mocker.Mock()

    code = mocker.Mock(spec=Code)
    code.schedule_length = 5
    code.check_schedule = [
        [mocker.Mock(spec=Check)]
        for _ in range(code.schedule_length)]
    detector_schedule = [
        [mocker.Mock(spec=Detector)]
        for _ in range(code.schedule_length)]

    # ... set up even more data...
    round = 7
    relative_round = round % code.schedule_length
    observables = None

    # Call the method!
    compiler.compile_round(
        round, relative_round, detector_schedule, observables, tick, circuit, code)

    circuit.measurer.add_detectors.assert_called_with(
        detector_schedule[relative_round], round)


def test_compiler_compile_round_calls_multiply_observable_correctly(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    # Mock over submethods used by this method
    compiler.add_start_of_round_noise = mocker.Mock()
    compiler.syndrome_extractor = mocker.Mock(spec=SyndromeExtractor)
    tick = 100
    compiler.syndrome_extractor.extract_checks = mocker.Mock(
        return_value=tick + 10)

    # Add some mock data, as well as mock methods on them
    circuit = mocker.Mock(spec=Circuit)
    circuit.measurer = mocker.Mock(spec=Measurer)
    circuit.measurer.add_detectors = mocker.Mock()
    circuit.measurer.multiply_observable = mocker.Mock()

    code = mocker.Mock(spec=Code)
    code.schedule_length = 5
    code.check_schedule = [
        [mocker.Mock(spec=Check)]
        for _ in range(code.schedule_length)]
    detector_schedule = [
        [mocker.Mock(spec=Detector)]
        for _ in range(code.schedule_length)]

    # ... set up even more data...
    round = 7
    relative_round = round % code.schedule_length
    checks = [mocker.Mock(spec=Check) for _ in range(2)]
    observables = [mocker.Mock(spec=LogicalOperator) for _ in range(2)]
    for check, observable in zip(checks, observables):
        observable.update = mocker.Mock(return_value=[check])

    # Call the method!
    compiler.compile_round(
        round, relative_round, detector_schedule, observables, tick, circuit, code)

    circuit.measurer.multiply_observable.assert_has_calls([
        mocker.call([check], observable, round)
        for check, observable in zip(checks, observables)])


def test_compiler_add_start_of_round_noise_does_nothing_when_no_noise(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    compiler.noise_model = NoNoise()

    # Explicit test
    tick = 0
    circuit = mocker.Mock(spec=Circuit)
    code = mocker.Mock(spec=Code)
    compiler.add_start_of_round_noise(tick, circuit, code)

    # Assert nothing happens!
    circuit.add_instruction.assert_not_called()


def test_compiler_add_start_of_round_noise_works_otherwise(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    compiler.noise_model = PhenomenologicalNoise(
        data_qubit=0.1, measurement=None)

    # Explicit test
    tick = 0
    circuit = mocker.Mock(spec=Circuit)
    data_qubits = {i: Qubit(i) for i in range(10)}
    code = mocker.Mock(spec=Code)
    code.data_qubits = data_qubits
    compiler.add_start_of_round_noise(tick, circuit, code)

    # Assert noise added to data qubits.
    noise = compiler.noise_model.data_qubit_start_round
    circuit.add_instruction.assert_has_calls([
        mocker.call(tick, MockInstruction(
            [qubit], noise.name, noise.params, is_noise=True))
        for qubit in data_qubits.values()])


def test_compiler_compile_final_measurements_gets_final_measurements_if_final_stabilizers_given(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    # Mock over the submethods used by the methods
    compiler.get_measurement_bases = mocker.Mock(return_value=[])
    compiler.measure_qubits = mocker.Mock()
    compiler.compile_final_detectors = mocker.Mock()
    compiler.compile_final_logical_operators = mocker.Mock()

    # Set up data
    # Make sure final_measurements is None but final_stabilizers isn't
    final_measurements = None
    final_stabilizers = []
    observables = None
    layer = 10
    tick = 100
    circuit = mocker.Mock(spec=Circuit)
    code = mocker.Mock(spec=Code)
    code.schedule_length = 10

    # Call the method
    compiler.compile_final_measurements(
        final_measurements,
        final_stabilizers,
        observables,
        layer,
        tick,
        circuit,
        code)

    compiler.get_measurement_bases.assert_called_with(final_stabilizers)


def test_compiler_compile_final_measurements_does_nothing_if_neither_final_measurements_nor_stabilizers_given(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    # Mock over the submethods used by the methods
    compiler.get_measurement_bases = mocker.Mock(return_value=[])
    compiler.measure_qubits = mocker.Mock()
    compiler.compile_final_detectors = mocker.Mock()
    compiler.compile_final_logical_operators = mocker.Mock()

    # Set up data
    # Make sure both final_measurements and final_stabilizers are None
    final_measurements = None
    final_stabilizers = None
    observables = None
    layer = 10
    tick = 100
    circuit = mocker.Mock(spec=Circuit)
    code = mocker.Mock(spec=Code)
    code.schedule_length = 10

    # Call the method
    compiler.compile_final_measurements(
        final_measurements,
        final_stabilizers,
        observables,
        layer,
        tick,
        circuit,
        code)

    compiler.measure_qubits.assert_not_called()
    compiler.compile_final_detectors.assert_not_called()
    compiler.compile_final_logical_operators.assert_not_called()


def test_compiler_compile_final_measurements_calls_measure_qubits_correctly(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    # Mock over the submethods used by the methods
    compiler.get_measurement_bases = mocker.Mock(return_value=[])
    compiler.measure_qubits = mocker.Mock()
    compiler.compile_final_detectors = mocker.Mock()
    compiler.compile_final_logical_operators = mocker.Mock()

    # Set up data
    qubit = Qubit(0)
    final_measurements = [Pauli(qubit, PauliLetter('Z'))]
    final_stabilizers = None
    observables = None
    layer = 10
    tick = 100
    circuit = mocker.Mock(spec=Circuit)
    code = mocker.Mock(spec=Code)
    code.schedule_length = 10

    # Call the method
    compiler.compile_final_measurements(
        final_measurements,
        final_stabilizers,
        observables,
        layer,
        tick,
        circuit,
        code)

    expected_checks = [Check([Pauli(qubit, PauliLetter('Z'))])]
    expected_round = layer * code.schedule_length
    # For some reason using assert_called_with doesn't work here,
    # so let's check each argument individually.
    compiler.measure_qubits.assert_called_once()
    assert compiler.measure_qubits.call_args_list[0].args[0] == final_measurements
    assert list(compiler.measure_qubits.call_args_list[0].args[1]) == expected_checks
    assert compiler.measure_qubits.call_args_list[0].args[2] == expected_round
    assert compiler.measure_qubits.call_args_list[0].args[3] == tick
    assert compiler.measure_qubits.call_args_list[0].args[4] == circuit


def test_compiler_compile_final_measurements_calls_compile_final_detectors_correctly(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    # Mock over the submethods used by the methods
    compiler.get_measurement_bases = mocker.Mock(return_value=[])
    compiler.measure_qubits = mocker.Mock()
    compiler.compile_final_detectors = mocker.Mock()
    compiler.compile_final_logical_operators = mocker.Mock()

    # Set up data
    qubit = Qubit(0)
    final_measurements = [Pauli(qubit, PauliLetter('Z'))]
    final_stabilizers = None
    observables = None
    layer = 10
    tick = 100
    circuit = mocker.Mock(spec=Circuit)
    code = mocker.Mock(spec=Code)
    code.schedule_length = 10

    # Call the method
    compiler.compile_final_measurements(
        final_measurements,
        final_stabilizers,
        observables,
        layer,
        tick,
        circuit,
        code)

    expected_checks = {qubit: Check([Pauli(qubit, PauliLetter('Z'))])}
    compiler.compile_final_detectors.assert_called_with(
        expected_checks, final_stabilizers, layer, circuit, code)


def test_compiler_compile_final_measurements_calls_compile_final_logical_operators_correctly(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    # Mock over the submethods used by the methods
    compiler.get_measurement_bases = mocker.Mock(return_value=[])
    compiler.measure_qubits = mocker.Mock()
    compiler.compile_final_detectors = mocker.Mock()
    compiler.compile_final_logical_operators = mocker.Mock()

    # Set up data
    qubit = Qubit(0)
    final_measurements = [Pauli(qubit, PauliLetter('Z'))]
    final_stabilizers = None
    observables = [mocker.Mock(spec=LogicalOperator)]
    layer = 10
    tick = 100
    circuit = mocker.Mock(spec=Circuit)
    code = mocker.Mock(spec=Code)
    code.schedule_length = 10

    # Call the method
    compiler.compile_final_measurements(
        final_measurements,
        final_stabilizers,
        observables,
        layer,
        tick,
        circuit,
        code)

    expected_checks = {qubit: Check([Pauli(qubit, PauliLetter('Z'))])}
    expected_round = layer * code.schedule_length
    compiler.compile_final_logical_operators.assert_called_with(
        observables, expected_checks, expected_round, circuit)


def test_compiler_compile_final_detectors_uses_stabilizers_when_given(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    compiler.compile_final_detectors_from_stabilizers = mocker.Mock()
    compiler.compile_final_detectors_from_measurements = mocker.Mock()

    # Set final stabilizers to None
    final_checks = {}
    final_stabilizers = None
    layer = 10

    # Create mock objects as needed
    circuit = mocker.Mock(spec=Circuit)
    circuit.measurer = mocker.Mock(spec=Measurer)
    code = mocker.Mock(spec=Code)
    code.schedule_length = 5

    # Call the method
    compiler.compile_final_detectors(
        final_checks, final_stabilizers, layer, circuit, code)

    # Assert the right helper method was used
    compiler.compile_final_detectors_from_stabilizers.assert_not_called()
    compiler.compile_final_detectors_from_measurements.assert_called_with(
        final_checks, 50, code)


def test_compiler_compile_final_detectors_uses_measurements_otherwise(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    compiler.compile_final_detectors_from_stabilizers = mocker.Mock()
    compiler.compile_final_detectors_from_measurements = mocker.Mock()

    # Set final checks to None
    final_checks = None
    final_stabilizers = []
    layer = 10

    # Create mock objects as needed
    circuit = mocker.Mock(spec=Circuit)
    circuit.measurer = mocker.Mock(spec=Measurer)
    code = mocker.Mock(spec=Code)
    code.schedule_length = 5

    # Call the method
    compiler.compile_final_detectors(
        final_checks, final_stabilizers, layer, circuit, code)

    # Assert the right helper method was used
    compiler.compile_final_detectors_from_stabilizers.assert_called_with(
        final_checks, final_stabilizers, code)
    compiler.compile_final_detectors_from_measurements.assert_not_called()


def test_compiler_compile_final_detectors_adds_detectors(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    compiler.compile_final_detectors_from_stabilizers = mocker.Mock(
        return_value=[])
    compiler.compile_final_detectors_from_measurements = mocker.Mock(
        return_value=[])

    # Create data needed to call the method
    final_checks = {}
    final_stabilizers = None
    layer = 10
    circuit = mocker.Mock(spec=Circuit)
    circuit.measurer = mocker.Mock(spec=Measurer)
    circuit.measurer.add_detectors = mocker.Mock()
    code = mocker.Mock(spec=Code)
    code.schedule_length = 5

    # Call the method
    compiler.compile_final_detectors(
        final_checks, final_stabilizers, layer, circuit, code)

    circuit.measurer.add_detectors.assert_called_with([], 50)


def test_compiler_compile_final_detectors_from_measurements_returns_empty_list_when_no_open_lids(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    code = mocker.Mock(spec=Code)
    code.schedule_length = 10

    # Set up a detector with a closed lid
    detector = mocker.Mock(spec=Drum)
    detector.has_open_lid = mocker.Mock(return_value=(False, None))
    code.detectors = [detector]

    # Imagine we measure data qubits in Z basis at the end
    qubits = [Qubit(0), Qubit(1)]
    final_checks = {
        qubit: Check([Pauli(qubit, PauliLetter('Z'))])
        for qubit in qubits}

    final_detectors = compiler.compile_final_detectors_from_measurements(
        final_checks, 0, code)
    assert final_detectors == []


def test_compiler_compile_final_detectors_from_measurements_returns_empty_list_when_open_lid_has_wrong_product(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    code = mocker.Mock(spec=Code)
    code.schedule_length = 10
    qubits = [Qubit(0), Qubit(1)]

    # Set up a detector whose floor has product XX
    detector = mocker.Mock(spec=Drum)
    detector_check = Check([
        Pauli(qubit, PauliLetter('X')) for qubit in qubits])
    detector_checks = [(-1, detector_check)]
    detector.has_open_lid = mocker.Mock(return_value=(True, detector_checks))
    code.detectors = [detector]

    # Imagine we measure data qubits in Z basis at the end
    final_checks = {
        qubit: Check([Pauli(qubit, PauliLetter('Z'))])
        for qubit in qubits}

    # No detector should be built, because one can't stick a ZZ lid on an XX floor.
    final_detectors = compiler.compile_final_detectors_from_measurements(
        final_checks, 0, code)
    assert final_detectors == []


def test_compiler_compile_final_detectors_from_measurements_builds_detector_otherwise(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    final_detector = mocker.Mock()
    drum_initialiser = mocker.Mock(return_value=final_detector)
    monkeypatch.setattr(
        'main.compiling.compilers.Compiler.Drum',
        drum_initialiser)

    code = mocker.Mock(spec=Code)
    code.schedule_length = 10
    qubits = [Qubit(0), Qubit(1)]

    # Set up a detector whose floor has product ZZ
    detector = mocker.Mock(spec=Drum)
    detector.lid_end = 2
    detector.anchor = None
    detector_check = Check([
        Pauli(qubit, PauliLetter('Z')) for qubit in qubits])
    # Suppose this check is measured 4 rounds before the last check in the lid
    detector_checks = [(-4, detector_check)]
    detector.has_open_lid = mocker.Mock(return_value=(True, detector_checks))
    code.detectors = [detector]

    # Imagine we measure data qubits in Z basis at the end
    final_checks = {
        qubit: Check([Pauli(qubit, PauliLetter('Z'))])
        for qubit in qubits}

    # Should be able to build a final ZZ detector!
    final_detectors = compiler.compile_final_detectors_from_measurements(
        final_checks, 0, code)

    # Check the detector is actually the one we were expecting
    expected_floor = [(-2, detector_check)]
    expected_lid = [(0, final_check) for final_check in final_checks.values()]
    drum_initialiser.assert_called_with(
        expected_floor, expected_lid, 0, detector.anchor)

    assert final_detectors == [final_detector]


def test_compiler_compile_final_detectors_from_stabilizers(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    code = mocker.Mock(spec=Code)
    code.schedule_length = 3
    qubits = [Qubit(0), Qubit(1)]
    final_checks = {
        qubit: Check([Pauli(qubit, PauliLetter('Z'))])
        for qubit in qubits}
    check_in_final_stabilizer = Check([
        Pauli(qubit, PauliLetter('Z')) for qubit in qubits])
    # Suppose the check in this stabilizer is measured in the last round
    # of the code's check schedule
    final_stabilizers = [Stabilizer([(0, check_in_final_stabilizer)], 2)]

    result = compiler.compile_final_detectors_from_stabilizers(
        final_checks, final_stabilizers, code)

    assert len(result) == 1
    final_detector = result[0]
    assert final_detector.floor == [(-1, check_in_final_stabilizer)]
    assert final_detector.lid == [
        (0, final_check) for final_check in final_checks.values()]
    assert final_detector.end == 0


def test_compiler_compile_final_detectors_from_stabilizers_raises_error_if_floor_and_lid_mismatch(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    code = mocker.Mock(spec=Code)
    code.schedule_length = 3
    qubits = [Qubit(0), Qubit(1)]
    # Measure all data qubits in X basis...
    final_checks = {
        qubit: Check([Pauli(qubit, PauliLetter('X'))])
        for qubit in qubits}
    # ... but try to build a detector with a ZZ floor
    check_in_final_stabilizer = Check([
        Pauli(qubit, PauliLetter('Z')) for qubit in qubits])
    final_stabilizers = [Stabilizer([(0, check_in_final_stabilizer)], 2)]

    expected_error = \
        "Can't create a Drum where the floor and lid don't compare the same " \
        "two Pauli products at different timesteps \(up to sign\)"
    with pytest.raises(ValueError, match=expected_error):
        compiler.compile_final_detectors_from_stabilizers(
            final_checks, final_stabilizers, code)


def test_compiler_measure_qubits_defaults_to_compiler_measurement_instructions(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler_measurement_instructions = {
        PauliLetter('Z'): ['MZ'],
        PauliLetter('X'): ['H', 'MZ']}
    compiler = Compiler(
        noise_model=NoNoise(),
        measurement_instructions=compiler_measurement_instructions)
    compiler.compile_gates = mocker.Mock(
        side_effect=lambda gates, _, __: 2 * len(gates))

    # Explicit test
    qubits = [Qubit(0), Qubit(1)]
    paulis = [
        Pauli(qubits[0], PauliLetter('Z')),
        Pauli(qubits[1], PauliLetter('X'))]
    checks = [mocker.Mock(spec=Check) for _ in paulis]
    circuit = mocker.Mock(spec=Circuit)
    tick = 0
    round = 0
    compiler.measure_qubits(paulis, checks, round, tick, circuit)

    # Assert compiler measurement instructions were used:
    measurements = [
        MockInstruction(qubits[:1], 'MZ', is_measurement=True),
        MockInstruction(qubits[1:], 'MZ', is_measurement=True)]
    circuit.measure.assert_has_calls([
        mocker.call(measurements[0], checks[0], round, 0),
        mocker.call(measurements[1], checks[1], round, 2)])
    compiler.compile_gates.assert_any_call(
        [MockInstruction(qubits[1:], 'H')], tick, circuit)


def test_compiler_measure_qubits_otherwise_uses_given_measurement_instructions(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler_measurement_instructions = {
        PauliLetter('Z'): ['MZ'],
        PauliLetter('X'): ['H', 'MZ']}
    compiler = Compiler(
        noise_model=NoNoise(),
        measurement_instructions=compiler_measurement_instructions)
    compiler.compile_gates = mocker.Mock(
        side_effect=lambda gates, _, __: 2 * len(gates))

    # Explicit test
    qubits = [Qubit(0), Qubit(1)]
    paulis = [
        Pauli(qubits[0], PauliLetter('Z')),
        Pauli(qubits[1], PauliLetter('X'))]
    checks = [mocker.Mock(spec=Check) for _ in paulis]
    circuit = mocker.Mock(spec=Circuit)
    tick = 0
    round = 0
    measurement_instructions = {
        PauliLetter('Z'): ['H', 'MX'],
        PauliLetter('X'): ['MX']}
    compiler.measure_qubits(
        paulis, checks, round, tick, circuit, measurement_instructions)

    # Assert given measurement instructions were used:
    measurements = [
        MockInstruction(qubits[:1], 'MX', is_measurement=True),
        MockInstruction(qubits[1:], 'MX', is_measurement=True)]
    circuit.measure.assert_has_calls([
        mocker.call(measurements[0], checks[0], round, 2),
        mocker.call(measurements[1], checks[1], round, 0)])
    compiler.compile_gates.assert_any_call(
        [MockInstruction(qubits[:1], 'H')], tick, circuit)


def test_compiler_measure_qubits_applies_measurement_noise_correctly(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    noise_model = PhenomenologicalNoise(measurement=0.1)
    compiler = Compiler(noise_model=noise_model)

    # Explicit test
    qubits = [Qubit(0), Qubit(1)]
    paulis = [
        Pauli(qubits[0], PauliLetter('Z')),
        Pauli(qubits[1], PauliLetter('X'))]
    checks = [mocker.Mock(spec=Check) for _ in paulis]
    circuit = mocker.Mock(spec=Circuit)
    tick = 0
    round = 0
    measurement_instructions = {
        PauliLetter('Z'): ['H', 'MX'],
        PauliLetter('X'): ['MX']}
    compiler.measure_qubits(
        paulis, checks, round, tick, circuit, measurement_instructions)

    # Assert given measurement instructions were used:
    measurements = [
        MockInstruction(qubits[:1], 'MX', 0.1, is_measurement=True),
        MockInstruction(qubits[1:], 'MX', 0.1, is_measurement=True)]
    circuit.measure.assert_has_calls([
        mocker.call(measurements[0], checks[0], round, 2),
        mocker.call(measurements[1], checks[1], round, 0)])


def test_compiler_measure_qubits_returns_correct_tick(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    compiler.compile_gates = mocker.Mock(
        side_effect=lambda gates, _, __: 2 * len(gates))

    # Explicit test
    qubits = [Qubit(0), Qubit(1)]
    paulis = [
        Pauli(qubits[0], PauliLetter('Z')),
        Pauli(qubits[1], PauliLetter('X'))]
    checks = [mocker.Mock(spec=Check) for _ in paulis]
    circuit = mocker.Mock(spec=Circuit)
    tick = 0
    round = 0
    measurement_instructions = {
        PauliLetter('Z'): ['H', 'MX'],
        PauliLetter('X'): ['MX']}
    next_tick = compiler.measure_qubits(
        paulis, checks, round, tick, circuit, measurement_instructions)

    # Assert circuit returns correct tick:
    assert next_tick == tick + 4


def test_compiler_compile_gates_fails_if_gate_size_not_one_or_two(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    expected_error = 'Can only compile one- or two-qubit gates'

    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    # An explicit test
    qubits = [Qubit(i) for i in range(3)]
    tick = 0
    circuit = mocker.Mock(spec=Circuit)
    gate = mocker.Mock(spec=Instruction)
    gate.qubits = qubits

    with pytest.raises(ValueError, match=expected_error):
        compiler.compile_gates([gate], tick, circuit)

    # Random tests
    for i in range(default_test_repeats_small):
        num_qubits = 10
        qubits = [Qubit(i) for i in range(num_qubits)]
        num_gates = random.randint(1, 10)
        gate_sizes = [random.randint(1, 10) for _ in range(num_gates)]
        if all([size <= 2 for size in gate_sizes]):
            break
        gate_qubit_indexes = [
            random.sample(range(num_qubits), k=size) for size in gate_sizes]
        gates = [mocker.Mock(spec=Instruction) for _ in range(num_gates)]
        for gate, indexes in zip(gates, gate_qubit_indexes):
            gate.qubits = [qubits[i] for i in indexes]

        tick = random.randint(0, 100)
        circuit = mocker.Mock(spec=Circuit)
        with pytest.raises(ValueError, match=expected_error):
            compiler.compile_gates(gates, tick, circuit)


def test_compiler_compile_gates_when_noise_is_none(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    compiler.noise_model = NoNoise()

    # An explicit test
    qubits = [Qubit(i) for i in range(3)]
    tick = 0
    circuit = mocker.Mock(spec=Circuit)
    gates = [
        Instruction(qubits[:1], 'ONE_QUBIT_GATE'),
        Instruction(qubits[1:], 'TWO_QUBIT_GATE')]
    next_tick = compiler.compile_gates(gates, tick, circuit)

    circuit.add_instruction.assert_has_calls([
        mocker.call(tick, gates[0]),
        mocker.call(tick + 2, gates[1])])
    assert next_tick == tick + 2 * len(gates)


def test_compiler_compile_gates_when_noise_not_none(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()
    one_qubit_noise_param = 0.1
    two_qubit_noise_param = 0.2
    compiler.noise_model = CircuitLevelNoise(
        one_qubit_gate=one_qubit_noise_param,
        two_qubit_gate=two_qubit_noise_param)

    # An explicit test
    qubits = [Qubit(i) for i in range(3)]
    tick = 0
    circuit = mocker.Mock(spec=Circuit)
    gates = [
        Instruction(qubits[:1], 'ONE_QUBIT_GATE'),
        Instruction(qubits[1:], 'TWO_QUBIT_GATE')]
    next_tick = compiler.compile_gates(gates, tick, circuit)

    one_qubit_noise = compiler.noise_model.one_qubit_gate
    expected_one_qubit_noise_instruction = MockInstruction(
        qubits[:1], one_qubit_noise.name, one_qubit_noise.params, is_noise=True)
    two_qubit_noise = compiler.noise_model.two_qubit_gate
    expected_two_qubit_noise_instruction = MockInstruction(
        qubits[1:], two_qubit_noise.name, two_qubit_noise.params, is_noise=True)

    circuit.add_instruction.assert_has_calls([
        mocker.call(tick, gates[0]),
        mocker.call(tick + 1, expected_one_qubit_noise_instruction),
        mocker.call(tick + 2, gates[1]),
        mocker.call(tick + 3, expected_two_qubit_noise_instruction)])
    assert next_tick == tick + 2 * len(gates)


def test_compiler_compile_final_logical_operators_raises_error_if_final_checks_wrong(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    # Explicit test
    qubit = Qubit(0)
    observable = LogicalOperator([Pauli(qubit, PauliLetter('Z'))])
    check = Check([Pauli(qubit, PauliLetter('X'))])
    final_checks = {qubit: check}
    round = 0
    circuit = mocker.Mock(spec=Circuit)

    expected_error = "Expected to include a final measurement of"
    with pytest.raises(ValueError, match=expected_error):
        compiler.compile_final_logical_operators(
            [observable], final_checks, round, circuit)


def test_compiler_compile_final_logical_operators_does_not_raise_error_if_final_checks_only_wrong_up_to_sign(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    # Explicit test
    qubit = Qubit(0)
    observable = LogicalOperator([Pauli(qubit, PauliLetter('Z'))])
    check = Check([Pauli(qubit, PauliLetter('Z', sign=-1))])
    final_checks = {qubit: check}
    round = 0
    circuit = mocker.Mock(spec=Circuit)
    circuit.measurer = mocker.Mock(spec=Measurer)

    compiler.compile_final_logical_operators(
        [observable], final_checks, round, circuit)
    circuit.measurer.multiply_observable.assert_called_with(
        [check], observable, round)


def test_compiler_compile_final_logical_operators_works_otherwise(
        monkeypatch: MonkeyPatch, mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate a Compiler
    monkeypatch.setattr(Compiler, '__abstractmethods__', set())
    compiler = Compiler()

    # Explicit test
    qubits = [Qubit(i) for i in range(3)]
    observable = LogicalOperator(
        [Pauli(qubit, PauliLetter('Z')) for qubit in qubits])
    checks = [Check([Pauli(qubit, PauliLetter('Z'))]) for qubit in qubits]
    final_checks = dict(zip(qubits, checks))
    round = 10
    circuit = mocker.Mock(spec=Circuit)
    circuit.measurer = mocker.Mock(spec=Measurer)

    compiler.compile_final_logical_operators(
        [observable], final_checks, round, circuit)
    circuit.measurer.multiply_observable.assert_called_with(
        checks, observable, round)


def test_compile_initialisation():
    _, _, circuit = test_compiler.compile_initialisation(
        rep_code, rep_initials_zero, None
    )
    assert circuit.instructions[0][rep_code.data_qubits[0]][0].name == "RZ"
    assert circuit.instructions[1][rep_code.data_qubits[2]][0].name == "PAULI_CHANNEL_1"

    _, _, circuit = test_compiler.compile_initialisation(
        rep_code, rep_initials_plus, None
    )
    assert circuit.instructions[0][rep_code.data_qubits[0]][0].name == "RX"
    assert circuit.instructions[1][rep_code.data_qubits[0]][0].name == "PAULI_CHANNEL_1"

    expected_message = \
        f"Set of data qubits whose initial states were either given " \
        f"or could be determined differs from the set of all data qubits."
    with pytest.raises(ValueError, match=expected_message):
        test_compiler.compile_initialisation(rep_code, {}, None)


def test_compile_layer():
    code = RotatedSurfaceCode(3)
    expected_instructions_per_tick = [17, 9, 12, 12, 12, 12, 8]
    syndrome_extractor = CxCyCzExtractor(RotatedSurfaceCodeOrderer())
    noise_model = CodeCapacityBitFlipNoise(0.1)

    rsc_qubits = list(code.data_qubits.values())
    rsc_initials = {qubit: State.Zero for qubit in rsc_qubits}
    compiler = AncillaPerCheckCompiler(noise_model, syndrome_extractor)
    initial_detector_schedules, tick, circuit = compiler.compile_initialisation(
        code, rsc_initials, None
    )

    # In this test, compile first syndrome extraction round at time tick - 2!
    # Means more inits are done in parallel.
    compiler.compile_layer(
        0,
        initial_detector_schedules[0],
        [code.logical_qubits[0].z],
        tick - 2,
        circuit,
        code,
    )
    instructions_per_tick = [
        len(tick_instructions) for tick_instructions in circuit.instructions.values()
    ]
    assert instructions_per_tick == expected_instructions_per_tick


def test_compile_final_measurement():
    code = RotatedSurfaceCode(3)
    expected_instructions_per_tick = [17, 9, 12, 12, 12, 12, 17]
    syndrome_extractor = CxCyCzExtractor(RotatedSurfaceCodeOrderer())
    noise_model = CodeCapacityBitFlipNoise(0.1)

    rsc_qubits = list(code.data_qubits.values())
    rsc_initials = {qubit: State.Zero for qubit in rsc_qubits}
    compiler = AncillaPerCheckCompiler(noise_model, syndrome_extractor)
    initial_detector_schedules, tick, circuit = compiler.compile_initialisation(
        code, rsc_initials, None
    )
    rsc_finals = [Pauli(qubit, PauliLetter('Z')) for qubit in rsc_qubits]
    tick = compiler.compile_layer(
        0,
        initial_detector_schedules[0],
        [code.logical_qubits[0].z],
        tick - 2,
        circuit,
        code,
    )
    # Similar to above, compile final measurements at time tick-2.
    # Means more measurements are done in parallel (data qubits and ancillas)
    compiler.compile_final_measurements(
        rsc_finals,
        None,
        [code.logical_qubits[0].z],
        1,
        tick - 2,
        circuit,
        code,
    )
    instructions_per_tick = [
        len(tick_instructions) for tick_instructions in circuit.instructions.values()
    ]
    assert instructions_per_tick == expected_instructions_per_tick


@pytest.mark.parametrize(
    "code, distance, num_detectors, num_measurements",
    [
        (RotatedSurfaceCode(3), 3, 24, 33),
        (RotatedSurfaceCode(5), 5, 120, 145),
    ],
)
def test_compile_code(code, distance, num_detectors, num_measurements):
    syndrome_extractor = CxCyCzExtractor(RotatedSurfaceCodeOrderer())
    p = 0.1
    noise_model = CodeCapacityBitFlipNoise(0.1)
    compiler = AncillaPerCheckCompiler(noise_model, syndrome_extractor)

    rsc_qubits = list(code.data_qubits.values())
    rsc_initials = {qubit: State.Zero for qubit in rsc_qubits}
    rsc_finals = [Pauli(qubit, PauliLetter('Z')) for qubit in rsc_qubits]
    rsc_logicals = [code.logical_qubits[0].z]
    rsc_circuit: stim.Circuit = compiler.compile_to_stim(
        code,
        distance,
        initial_states=rsc_initials,
        final_measurements=rsc_finals,
        observables=rsc_logicals,
    )
    assert rsc_circuit.num_detectors == num_detectors

    # 8 + 8 + 17 = 3
    assert rsc_circuit.num_measurements == num_measurements
    assert len(rsc_circuit.shortest_graphlike_error()) == distance

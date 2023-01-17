import random

import stim
import pytest
from _pytest.monkeypatch import MonkeyPatch
from pytest_mock import MockerFixture

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.Code import Code
from main.compiling.Circuit import Circuit
from main.compiling.Instruction import Instruction
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.codes.RepetitionCode import RepetitionCode
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.compiling.compilers.Compiler import Compiler
from main.compiling.noise.models import CircuitLevelNoise, CodeCapacityBitFlipNoise, PhenomenologicalNoise
from main.compiling.noise.models.NoNoise import NoNoise
from main.compiling.syndrome_extraction.controlled_gate_orderers.RotatedSurfaceCodeOrderer import \
    RotatedSurfaceCodeOrderer
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import TrivialOrderer
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
# - compile_initialisation
# - X initialize_qubits
# - compile_layer
# - compile_round
# - X add_start_of_round_noise
# - compile_final_measurements
# - compile_final_detectors
# - compile_final_detectors_from_stabilizers
# - compile_final_detectors_from_measurements
# - compile_initial_logical_observables
# - measure_qubits
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

    try:
        _, _, circuit = test_compiler.compile_initialisation(rep_code, {}, None)
        raise ValueError("Shouldn't be able to initialise if no states given.")
    except ValueError as error:
        expected_message = (
            "Some data qubits' initial states either aren't given or "
            "aren't determined by the given initial stabilizers! Please "
            "give a complete set of desired initial states or desired "
            "stabilizers for the first round of measurements."
        )
        assert str(error) == expected_message


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
        logical_observables=rsc_logicals,
    )
    assert rsc_circuit.num_detectors == num_detectors

    # 8 + 8 + 17 = 3
    assert rsc_circuit.num_measurements == num_measurements
    assert len(rsc_circuit.shortest_graphlike_error()) == distance

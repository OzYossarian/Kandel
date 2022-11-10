import stim
import pytest
from _pytest.monkeypatch import MonkeyPatch
from pytest_mock import MockerFixture

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.codes.RepetitionCode import RepetitionCode
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.compiling.compilers.Compiler import Compiler
from main.compiling.noise.models import CircuitLevelNoise, CodeCapacityBitFlipNoise
from main.compiling.noise.models.NoNoise import NoNoise
from main.compiling.syndrome_extraction.controlled_gate_orderers.RotatedSurfaceCodeOrderer import \
    RotatedSurfaceCodeOrderer
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import TrivialOrderer
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CnotExtractor import CnotExtractor
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
from main.utils.enums import State

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
# - initialize_qubits
# - compile_layer
# - compile_round
# - add_start_of_round_noise
# - compile_final_measurements
# - compile_final_detectors
# - compile_final_detectors_from_stabilizers
# - compile_final_detectors_from_measurements
# - compile_initial_logical_observables
# - measure_qubits
# - compile_one_qubit_gates
# - compile_two_qubit_gates
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


def test_compiler_compile_one_qubit_gates(monkeypatch: MonkeyPatch):
    pass


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

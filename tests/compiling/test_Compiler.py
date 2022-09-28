import stim
import pytest
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.codes.RepetitionCode import RepetitionCode
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.compiling.noise.models import CircuitLevelNoise, CodeCapacityBitFlipNoise
from main.compiling.syndrome_extraction.controlled_gate_orderers.RotatedSurfaceCodeOrderer import \
    RotatedSurfaceCodeOrderer
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import TrivialOrderer
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
from main.enums import State

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
rep_finals = [Pauli(qubit, PauliZ) for qubit in rep_qubits]
rep_logicals = [rep_code.logical_qubits[0].z]


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
    rsc_finals = [Pauli(qubit, PauliZ) for qubit in rsc_qubits]
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
    rsc_finals = [Pauli(qubit, PauliZ) for qubit in rsc_qubits]
    rsc_logicals = [code.logical_qubits[0].z]
    rsc_circuit: stim.Circuit = compiler.compile_code(
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

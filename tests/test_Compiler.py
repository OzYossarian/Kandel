import stim
import pytest
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ
from main.codes.ShortRotatedSurfaceCode import ShortRotatedSurfaceCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.compilers.Compiler import Compiler
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.codes.RepetitionCode import RepetitionCode
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.codes.ShortRotatedSurfaceCode import ShortRotatedSurfaceCode
from main.compiling.Circuit import Circuit
from main.compiling.noise.models import CircuitLevelNoise
from main.codes.hexagonal.tic_tac_toe.HoneycombCode import HoneycombCode
from main.compiling.noise.models.CodeCapacityBitFlipNoise import (
    CodeCapacityBitFlipNoise,
)
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import (
    TrivialOrderer,
)
from main.compiling.syndrome_extraction.controlled_gate_orderers.RotatedSurfaceCodeOrderer import (
    RotatedSurfaceCodeOrderer,
)
from main.compiling.syndrome_extraction.extractors.PurePauliWordExtractor import (
    PurePauliWordExtractor,
)
from main.enums import State
import stimcirq

test_qpu = SquareLatticeQPU((3, 1))
rep_code = RepetitionCode(2)
test_qpu.embed(rep_code, (0, 0), 0)
trivial_orderer = TrivialOrderer()
extractor = PurePauliWordExtractor(trivial_orderer)
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


@pytest.mark.parametrize(
    "code, n_instructions",
    [
        # 17 qubits initialized, 9 errors on data qubits, 4 * 6 cnots + 1 * 8 measurements
        (RotatedSurfaceCode(3), [17, 9, 12, 12, 12, 12, 8]),
        # 13 qubits initialized, 2 * (9 errors on data qubits, 4*3 cnots + 1 * 4 measurements)
        (ShortRotatedSurfaceCode(3), [13, 9, 6, 6, 6, 6, 4, 9, 4, 6, 6, 6, 6, 4]),
    ],
)
def test_compile_layer(code, n_instructions):
    syndrome_extractor = PurePauliWordExtractor(RotatedSurfaceCodeOrderer())
    p = 0.1
    noise_model = CodeCapacityBitFlipNoise(0.1)

    rsc_qubits = list(code.data_qubits.values())
    rsc_initials = {qubit: State.Zero for qubit in rsc_qubits}
    compiler = AncillaPerCheckCompiler(noise_model, syndrome_extractor)
    initial_detector_schedules, tick, circuit = compiler.compile_initialisation(
        code, rsc_initials, None
    )

    tick, circuit = compiler.compile_layer(
        0,
        initial_detector_schedules[0],
        [code.logical_qubits[0].z],
        tick - 2,
        circuit,
        code,
    )
    number_of_operations = []
    for index, layer in enumerate(circuit.instructions):
        number_of_operations.append(len(circuit.instructions[layer]))
    assert number_of_operations == n_instructions


def test_compile_final_measurement():
    code = RotatedSurfaceCode(3)
    syndrome_extractor = PurePauliWordExtractor(RotatedSurfaceCodeOrderer())
    p = 0.1
    noise_model = CodeCapacityBitFlipNoise(0.1)

    rsc_qubits = list(code.data_qubits.values())
    rsc_initials = {qubit: State.Zero for qubit in rsc_qubits}
    compiler = AncillaPerCheckCompiler(noise_model, syndrome_extractor)
    initial_detector_schedules, tick, circuit = compiler.compile_initialisation(
        code, rsc_initials, None
    )

    rsc_finals = [Pauli(qubit, PauliZ) for qubit in rsc_qubits]
    tick, circuit = compiler.compile_layer(
        0,
        initial_detector_schedules[0],
        [code.logical_qubits[0].z],
        tick - 2,
        circuit,
        code,
    )

    compiler.compile_final_measurements(
        rsc_finals,
        None,
        [code.logical_qubits[0].z],
        1,
        26,
        circuit,
        code,
    )
    number_of_operations = []
    for index, layer in enumerate(circuit.instructions):
        number_of_operations.append(len(circuit.instructions[layer]))
    assert number_of_operations == [17, 9, 12, 12, 12, 12, 17]


@pytest.mark.parametrize(
    "code, distance, num_detectors, num_measurements",
    [
        (RotatedSurfaceCode(3), 3, 24, 33),
        (RotatedSurfaceCode(5), 5, 120, 145),
#        (ShortRotatedSurfaceCode(3), 3, 24, 33),
        #        (ShortRotatedSurfaceCode(5), 5, 120, 145),
    ],
)
def test_compile_code(code, distance, num_detectors, num_measurements):
    syndrome_extractor = PurePauliWordExtractor(RotatedSurfaceCodeOrderer())
    p = 0.1
    noise_model = CircuitLevelNoise(
        initialisation=0.3, idling=p, one_qubit_gate=p, two_qubit_gate=p, measurement=p
    )

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
    print(
        stimcirq.stim_circuit_to_cirq_circuit(rsc_circuit),
        file=open("new_compiled.txt", "a"),
    )
    print(rsc_circuit.num_detectors, "num detectors")
    assert rsc_circuit.num_detectors == num_detectors

    # 8 + 8 + 17 = 3
    assert rsc_circuit.num_measurements == num_measurements
    assert len(rsc_circuit.shortest_graphlike_error()) == distance


# test_compile_code(RotatedSurfaceCode(3), 3, 12, 17)

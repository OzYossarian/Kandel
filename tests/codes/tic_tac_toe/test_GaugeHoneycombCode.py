from main.building_blocks.Check import Check
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.gauge.GaugeHoneycombCode import GaugeHoneycombCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.PhenomenologicalNoise import PhenomenologicalNoise
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
import stim
import itertools

from main.utils.enums import State


def generate_circuit_X_observable(rounds, distance, gauge_factors):
    code = GaugeHoneycombCode(distance, gauge_factors)
    logical_observables = [code.logical_qubits[1].x]
    initial_stabilizers = []
    for check in code.check_schedule[0]:
        initial_stabilizers.append(Stabilizer([(0, check)], 0))

    compiler = AncillaPerCheckCompiler(
        noise_model=PhenomenologicalNoise(OneQubitNoise(0.1, 0.1, 0.1), 0.1),
        syndrome_extractor=CxCyCzExtractor())
    stim_circuit = compiler.compile_to_stim(
        code=code,
        total_rounds=rounds,
        initial_stabilizers=initial_stabilizers,
        observables=logical_observables
    )
    return (stim_circuit)


def generate_circuit_Z_observable(rounds, distance, gauge_factors):

    code = GaugeHoneycombCode(distance, gauge_factors)
    logical_observables = [code.logical_qubits[0].z]
    initial_states = dict()
    for qubit in code.data_qubits.values():
        initial_states[qubit] = State(0)

    compiler = AncillaPerCheckCompiler(
        noise_model=PhenomenologicalNoise(0.1, 0.1),
        syndrome_extractor=CxCyCzExtractor())
    stim_circuit = compiler.compile_to_stim(
        code=code,
        total_rounds=rounds,
        initial_states=initial_states,
        observables=logical_observables
    )
    return (stim_circuit)


def check_for_5_detectors_violated(dem):
    for dem_instruction in dem:
        if dem_instruction.type == "error":
            error_targets = dem_instruction.targets_copy()
            n_violated_detectors = 0
            for target in error_targets:
                if target.is_relative_detector_id() == True:
                    n_violated_detectors += 1
            if n_violated_detectors == 5:
                return (False)
    return (True)


def check_parity_of_number_of_violated_detectors(circuit: stim.Circuit):
    assert check_for_5_detectors_violated(circuit.detector_error_model(
        approximate_disjoint_errors=True)) == True


def check_distance(circuit: stim.Circuit, distance):
    assert len(circuit.detector_error_model(
        approximate_disjoint_errors=True).shortest_graphlike_error()) == distance


def test_properties_of_d4_codes():
    for gauge_factors in itertools.product([1, 2, 3], repeat=3):
        for n_rounds in range(sum(gauge_factors)*2, sum(gauge_factors)*3):
            circuit: stim.Circuit = generate_circuit_X_observable(
                n_rounds, 4, gauge_factors)
            check_parity_of_number_of_violated_detectors(circuit)
            check_distance(circuit, 4)


def test_d4_codes_high_gauge():
    circuit: stim.Circuit = generate_circuit_X_observable(
        20, 4, [1, 1, 2])
    check_parity_of_number_of_violated_detectors(circuit)
    check_distance(circuit, 4)

    circuit: stim.Circuit = generate_circuit_X_observable(
        16, 4, [4, 1, 1])
    check_parity_of_number_of_violated_detectors(circuit)
    check_distance(circuit, 4)

    circuit: stim.Circuit = generate_circuit_X_observable(
        25, 4, [3, 2, 4])
    check_parity_of_number_of_violated_detectors(circuit)
    check_distance(circuit, 4)




def test_Z_observable():
    circuit: stim.Circuit = generate_circuit_Z_observable(12, 4, [1, 1, 1])
    check_parity_of_number_of_violated_detectors(circuit)
    check_distance(circuit, 4)



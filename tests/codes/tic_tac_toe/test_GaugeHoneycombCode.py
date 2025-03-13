from typing import Any, List, Tuple
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.codes.tic_tac_toe.gauge.GaugeHoneycombCode import GaugeHoneycombCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.compilers.NativePauliProductMeasurementsCompiler import NativePauliProductMeasurementsCompiler
from main.compiling.noise.models import EM3, PhenomenologicalNoise, StandardDepolarizingNoise
from main.compiling.syndrome_extraction.extractors import NativePauliProductMeasurementsExtractor
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
import stim
import itertools
import pytest
from typing import Literal


def generate_circuit(rounds, distance, gauge_factors, observable_type, noise_model=Literal['phenomenological_noise', 'circuit_level_noise', 'EM3']) -> Tuple[stim.Circuit, GaugeHoneycombCode]:
    code = GaugeHoneycombCode(distance, gauge_factors)
    if observable_type == 'memory_z':
        logical_observables = [code.logical_qubits[0].z]
        check_schedule_index = gauge_factors[0] + gauge_factors[1]
        final_measurements = None

    elif observable_type == 'memory_x':
        logical_observables = [code.logical_qubits[1].x]
        check_schedule_index = 0
        final_measurements = None

    elif observable_type == 'stability_x':
        logical_observables = [code.x_stability_operator]
        check_schedule_index = gauge_factors[0] + gauge_factors[1]
        final_measurements = code.get_possible_final_measurement(
            code.logical_qubits[1].z, rounds)
    elif observable_type == 'stability_z':
        logical_observables = [code.z_stability_operator]
        check_schedule_index = 0
        final_measurements = code.get_possible_final_measurement(
            code.logical_qubits[0].x, rounds)

    initial_stabilizers = [Stabilizer(
        [(0, check)], 0) for check in code.check_schedule[check_schedule_index]]

    if noise_model == 'phenomenological_noise':
        noise = PhenomenologicalNoise(
            0.1)
    elif noise_model == 'circuit_level_noise':
        noise = StandardDepolarizingNoise(
            0.1)

    if noise_model == 'EM3':
        noise = EM3(0.1)
        compiler = NativePauliProductMeasurementsCompiler(
            noise_model=noise,
            syndrome_extractor=NativePauliProductMeasurementsExtractor())
    else:
        compiler = AncillaPerCheckCompiler(
            noise_model=noise,
            syndrome_extractor=CxCyCzExtractor())

    stim_circuit = compiler.compile_to_stim(
        code=code,
        total_rounds=rounds,
        initial_stabilizers=initial_stabilizers,
        observables=logical_observables,
        final_measurements=final_measurements
    )
    return (stim_circuit, code)


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


def get_graphlike_distance(circuit: stim.Circuit) -> int:
    return len(circuit.detector_error_model(decompose_errors=True,
                                            approximate_disjoint_errors=True).shortest_graphlike_error())


def check_graphlike_distance(circuit: stim.Circuit, distance):
    assert len(circuit.detector_error_model(decompose_errors=True,
                                            approximate_disjoint_errors=True).shortest_graphlike_error()) == distance


def get_hyper_edge_distsance(circuit: stim.Circuit) -> int:
    logical_errors = circuit.search_for_undetectable_logical_errors(
        dont_explore_detection_event_sets_with_size_above=4,
        dont_explore_edges_with_degree_above=4,
        dont_explore_edges_increasing_symptom_degree=False,
    )

    return len(logical_errors)


def check_hyper_edge_distance(circuit: stim.Circuit, distance):
    logical_errors = circuit.search_for_undetectable_logical_errors(
        dont_explore_detection_event_sets_with_size_above=6,
        dont_explore_edges_with_degree_above=6,
        dont_explore_edges_increasing_symptom_degree=False,
        canonicalize_circuit_errors=True
    )
    assert len(logical_errors) == distance


@ pytest.mark.parametrize("noise_model, distance", [('phenomenological_noise', 4), ('circuit_level_noise', 4), ('EM3', 2)])
def test_memory_graphlike_distance_of_d4_codes(noise_model, distance):
    for gauge_factors in itertools.product([1, 2], repeat=3):
        for n_rounds in range(sum(gauge_factors)*2, sum(gauge_factors)*3):
            circuit: stim.Circuit
            circuit, _ = generate_circuit(
                n_rounds, 4, gauge_factors, 'memory_x', noise_model=noise_model)
            check_parity_of_number_of_violated_detectors(circuit)
            check_graphlike_distance(circuit, distance)


@ pytest.mark.parametrize("distance, gauge_factors, observable_type", [([8, 4], [1, 1, 1], 'memory_x'), ([4, 8], [1, 1, 1],  'memory_z')])
def test_rectangular_distances(distance, gauge_factors, observable_type):
    circuit, _ = generate_circuit(
        12, distance, gauge_factors, observable_type, noise_model='phenomenological_noise')

    check_graphlike_distance(
        circuit, distance[1] if observable_type == 'memory_z' else distance[1])


@ pytest.mark.parametrize("gauge_factors,n_rounds", [([4, 1, 1], 16), ([3, 2, 4], 25)])
def test_memory_graphlike_distance_high_gauge_d4_codes(gauge_factors, n_rounds):
    circuit: stim.Circuit
    circuit, _ = generate_circuit(
        n_rounds, 4, gauge_factors, 'memory_x', noise_model='phenomenological_noise')
    check_parity_of_number_of_violated_detectors(circuit)
    check_graphlike_distance(circuit, 4)

    circuit: stim.Circuit
    circuit, _ = generate_circuit(
        n_rounds, 4, gauge_factors, 'memory_z', noise_model='circuit_level_noise')
    check_parity_of_number_of_violated_detectors(circuit)
    check_graphlike_distance(circuit, 4)


@ pytest.mark.parametrize("gauge_factors,n_rounds", [([1, 1, 1], 19), ([1, 2, 1], 16), ([2, 2, 2], 20), ([2, 1, 2], 24)])
def test_get_timelike_distance(gauge_factors, n_rounds):
    code = GaugeHoneycombCode(4, gauge_factors)
    distance = code.get_timelike_distance(
        n_rounds, "X", noise_model="circuit_level_noise")
    circ, _ = generate_circuit(
        n_rounds, 4, gauge_factors, 'stability_x', noise_model='circuit_level_noise')

    check_graphlike_distance(circ, distance)


@ pytest.mark.parametrize("timelike_distance", [4, 5])
def test_get_number_of_rounds_for_stability_experiment(timelike_distance):
    code = GaugeHoneycombCode(4, [2, 1, 2])
    rounds, distance_x, distance_z = code.get_number_of_rounds_for_timelike_distance(
        timelike_distance, noise_model='circuit_level_noise')
    circ_z, _ = generate_circuit(
        rounds, 4, [2, 1, 2], 'stability_z', noise_model='circuit_level_noise')
    check_hyper_edge_distance(circ_z, distance_z)
    circ_x, _ = generate_circuit(
        rounds, 4, [2, 1, 2], 'stability_x', noise_model='circuit_level_noise')
    check_hyper_edge_distance(circ_x, distance_x)
    circ_x_short, _ = generate_circuit(
        rounds-1, 4, [2, 1, 2], 'stability_x', noise_model='circuit_level_noise')
    circ_z_short, _ = generate_circuit(
        rounds-1, 4, [2, 1, 2], 'stability_z', noise_model='circuit_level_noise')

    assert get_hyper_edge_distsance(
        circ_x_short) < timelike_distance or get_hyper_edge_distsance(circ_z_short) < timelike_distance


@ pytest.mark.parametrize("gauge_factors,timelike_distance,distance", [([1, 1, 1], 4, 4), ([1, 2, 1], 7, 4),
                                                                       ([2, 2, 2], 8, 4), ([
                                                                           2, 1, 2], 9, 4),
                                                                       ([1, 1, 1], 7, 8), ([3, 3, 3], 5, 4)])
def test_get_number_of_rounds_for_stability_experiment_graphlike(gauge_factors, timelike_distance, distance):
    code = GaugeHoneycombCode(distance, gauge_factors)
    rounds, distance_x, distance_z = code.get_number_of_rounds_for_timelike_distance(
        timelike_distance, graphlike=True, noise_model='circuit_level_noise')
    circ_z, _ = generate_circuit(
        rounds, distance, gauge_factors, 'stability_z', noise_model='circuit_level_noise')
    circ_x, _ = generate_circuit(
        rounds, distance, gauge_factors, 'stability_x', noise_model='circuit_level_noise')
    check_graphlike_distance(circ_z, distance_z)
    check_graphlike_distance(circ_x, distance_x)
    assert distance_x == timelike_distance or distance_z == timelike_distance
    circ_x_short, _ = generate_circuit(
        rounds-1, distance, gauge_factors, 'stability_x', noise_model='circuit_level_noise')
    circ_z_short, _ = generate_circuit(

        rounds-1, distance, gauge_factors, 'stability_z', noise_model='circuit_level_noise')

    assert get_graphlike_distance(
        circ_x_short) < timelike_distance or get_graphlike_distance(circ_z_short) < timelike_distance

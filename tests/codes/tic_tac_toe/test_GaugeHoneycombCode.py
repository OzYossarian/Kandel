import math
from typing import Any, List, Tuple
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
import pytest


def generate_circuit(rounds, distance, gauge_factors, observable_type, initial_stabilizers=None, measurement_error_probability=0.1, data_qubit_error_probability=0.1):
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

    compiler = AncillaPerCheckCompiler(
        noise_model=PhenomenologicalNoise(
            data_qubit_error_probability, measurement_error_probability),
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
    return len(circuit.detector_error_model(
        approximate_disjoint_errors=True).shortest_graphlike_error())


def check_graphlike_distance(circuit: stim.Circuit, distance):
    print(len(circuit.detector_error_model(
        approximate_disjoint_errors=True).shortest_graphlike_error())
    )
    assert len(circuit.detector_error_model(
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
        dont_explore_detection_event_sets_with_size_above=4,
        dont_explore_edges_with_degree_above=4,
        dont_explore_edges_increasing_symptom_degree=False,

    )
    assert len(logical_errors) == distance


def test_memory_graphlike_distance_of_d4_codes():
    for gauge_factors in itertools.product([1, 2], repeat=3):
        for n_rounds in range(sum(gauge_factors)*2, sum(gauge_factors)*3):
            circuit: stim.Circuit
            circuit, _ = generate_circuit(
                n_rounds, 4, gauge_factors, 'memory_x')
            check_parity_of_number_of_violated_detectors(circuit)
            check_graphlike_distance(circuit, 4)


def test_rectangular_distances():
    circuit: stim.Circuit
    circuit, _ = generate_circuit(12, [4, 8], [1, 1, 1], 'memory_x')
    check_graphlike_distance(circuit, 8)

    circuit, _ = generate_circuit(12, [8, 4], [1, 1, 1], 'memory_x')
    check_graphlike_distance(circuit, 4)

    circuit, _ = generate_circuit(12, [4, 8], [1, 1, 1], 'memory_z')
    check_graphlike_distance(circuit, 8)

    circuit, _ = generate_circuit(12, [8, 4], [1, 1, 1], 'memory_z')
    check_graphlike_distance(circuit, 4)


@pytest.mark.parametrize("gauge_factors,n_rounds", [([4, 1, 1], 16), ([3, 2, 4], 25)])
def test_memory_graphlike_distance_high_gauge_d4_codes(gauge_factors, n_rounds):
    circuit: stim.Circuit
    circuit, _ = generate_circuit(
        n_rounds, 4, gauge_factors, 'memory_x')
    check_parity_of_number_of_violated_detectors(circuit)
    check_graphlike_distance(circuit, 4)

    circuit: stim.Circuit
    circuit, _ = generate_circuit(
        n_rounds, 4, gauge_factors, 'memory_z')
    check_parity_of_number_of_violated_detectors(circuit)
    check_graphlike_distance(circuit, 4)


@pytest.mark.parametrize("gauge_factors,n_rounds", [([1, 2, 1], 16), ([2, 2, 2], 20), ([2, 1, 2], 24)])
def test_get_timelike_distance(gauge_factors, n_rounds):
    code = GaugeHoneycombCode(4, gauge_factors)
    distance = code.get_non_graphlike_timelike_distance(n_rounds, "X")
    circ, _ = generate_circuit(n_rounds, 4, gauge_factors, 'stability_x')
    check_hyper_edge_distance(circ, distance)


@pytest.mark.parametrize("timelike_distance", [6, 8, 9])
def test_get_number_of_rounds_for_stability_experiment(timelike_distance):
    code = GaugeHoneycombCode(4, [2, 1, 2])
    rounds, distance_x, distance_z = code.get_number_of_rounds_for_timelike_distance(
        timelike_distance, graphlike=False)
    circ_z, _ = generate_circuit(rounds, 4, [2, 1, 2], 'stability_z')
    check_hyper_edge_distance(circ_z, distance_z)
    circ_x, _ = generate_circuit(rounds, 4, [2, 1, 2], 'stability_x')
    check_hyper_edge_distance(circ_x, distance_x)
    circ_x_short, _ = generate_circuit(rounds-1, 4, [2, 1, 2], 'stability_x')
    circ_z_short, _ = generate_circuit(rounds-1, 4, [2, 1, 2], 'stability_z')

    assert get_hyper_edge_distsance(
        circ_x_short) < timelike_distance or get_hyper_edge_distsance(circ_z_short) < timelike_distance


@pytest.mark.parametrize("gauge_factors,timelike_distance,distance", [([1, 1, 1], 10, 4), ([1, 2, 1], 16, 4),
                                                                      ([2, 2, 2], 20, 4), ([
                                                                          2, 1, 2], 24, 4),
                                                                      ([1, 1, 1], 8, 8), ([3, 3, 3], 8, 9)])
def test_get_number_of_rounds_for_stability_experiment_graphlike(gauge_factors, timelike_distance, distance):
    code = GaugeHoneycombCode(distance, gauge_factors)
    rounds, distance_x, distance_z = code.get_number_of_rounds_for_timelike_distance(
        timelike_distance, graphlike=True)
    circ_z, _ = generate_circuit(
        rounds, distance, gauge_factors, 'stability_z')
    circ_x, _ = generate_circuit(
        rounds, distance, gauge_factors, 'stability_x')
    check_graphlike_distance(circ_z, distance_z)
    check_graphlike_distance(circ_x, distance_x)
    assert distance_x == timelike_distance or distance_z == timelike_distance
    circ_x_short, _ = generate_circuit(
        rounds-1, distance, gauge_factors, 'stability_x')
    circ_z_short, _ = generate_circuit(
        rounds-1, distance, gauge_factors, 'stability_z')
    assert get_graphlike_distance(
        circ_x_short) < timelike_distance or get_graphlike_distance(circ_z_short) < timelike_distance

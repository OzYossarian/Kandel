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
        check_schedule_index = gauge_factors[0] + gauge_factors[1]+1
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


def check_distance(circuit: stim.Circuit, distance):
    assert len(circuit.detector_error_model(
        approximate_disjoint_errors=True).shortest_graphlike_error()) == distance


def test_properties_of_d4_codes():
    for gauge_factors in itertools.product([1, 2, 3], repeat=3):
        for n_rounds in range(sum(gauge_factors)*2, sum(gauge_factors)*3):
            circuit: stim.Circuit
            circuit, code = generate_circuit(
                n_rounds, 4, gauge_factors, 'memory_x')
            check_parity_of_number_of_violated_detectors(circuit)
            check_distance(circuit, 4)


def test_d4_codes_high_gauge():
    circuit: stim.Circuit = generate_circuit(
        20, 4, [1, 1, 2], 'memory_x')
    check_parity_of_number_of_violated_detectors(circuit)
    check_distance(circuit, 4)

    circuit: stim.Circuit = generate_circuit(
        16, 4, [4, 1, 1], 'memory_x')
    check_parity_of_number_of_violated_detectors(circuit)
    check_distance(circuit, 4)

    circuit: stim.Circuit = generate_circuit(
        25, 4, [3, 2, 4], 'memory_x')
    check_parity_of_number_of_violated_detectors(circuit)
    check_distance(circuit, 4)


def test_Z_observable():
    circuit: stim.Circuit
    circuit, _ = generate_circuit(16, 4, [1, 1, 1], 'memory_z')
    check_parity_of_number_of_violated_detectors(circuit)
    check_distance(circuit, 4)


def distance_of_stability(rounds: int, letter: str) -> int:
    if letter == 'x':
        return (math.ceil((rounds-6)/3))
    elif letter == 'z':
        return (math.ceil((rounds-2)/3))


def remove_final_detectors(circuit: stim.Circuit) -> stim.Circuit:
    layer = len(circuit) - 1

    while layer >= 0:
        if circuit[layer].name != "DETECTOR":
            return (circuit[:(layer+1)])
        else:
            layer -= 1


def remove_detectors(circuit: stim.Circuit, layers_to_skip_detectors: List[int], length_of_route=int) -> stim.Circuit:
    vertical_layer = 0
    layer: stim.CircuitInstruction
    new_circuit = stim.Circuit()
    for layer in circuit:
        if layer.name == "SHIFT_COORDS":
            vertical_layer += 1

        if layer.name == "DETECTOR":

            if (vertical_layer % length_of_route) not in layers_to_skip_detectors:
                new_circuit.append(layer)
            elif vertical_layer == 16:
                new_circuit.append(layer)

        else:
            new_circuit.append(layer)

    new_circuit = remove_final_detectors(new_circuit)
    return (new_circuit)


def check_hyper_edge_distance(circuit: stim.Circuit, distance):

    logical_errors = circuit.search_for_undetectable_logical_errors(
        dont_explore_detection_event_sets_with_size_above=6,
        dont_explore_edges_with_degree_above=6,
        dont_explore_edges_increasing_symptom_degree=False,

    )

    assert len(logical_errors) == distance


def test_stability_x_measurement_noise_graphlike_distance():
    gauge_factors = [2, 2, 2]
    for n_rounds in range(12, 30, 1):

        circuit: stim.Circuit
        circuit, code = generate_circuit(
            n_rounds, 4, gauge_factors, 'stability_x', measurement_error_probability=0.1, data_qubit_error_probability=0)

        new_circuit = remove_detectors(
            circuit, [2, 3, 6, 7, 10, 11], sum(gauge_factors)*2)

        check_distance(
            new_circuit, 2*(n_rounds-5)//8+1)


def find_next_occurence(measurement_list: List, starting_index: int, letter: str) -> int:
    if letter not in measurement_list[starting_index:]:
        return -1
    else:
        return (measurement_list[starting_index:].index(letter) + starting_index)


def find_ending_index_of_set(measurement_list: List, starting_index: int, letter: str) -> int:
    first_letter_after_start = find_next_occurence(
        measurement_list, starting_index, letter)

    if first_letter_after_start == -1:
        # TODO this three is going to depend on gauge factors
        if len(measurement_list) - starting_index > 3:
            return len(measurement_list)
        else:
            return len(measurement_list)+1

    else:
        for i in range(first_letter_after_start, len(measurement_list)):
            if measurement_list[i] != letter:
                return i
        return len(measurement_list)


def distance_from_measurement_list(measurement_list: List, starting_letter: str, schedule_length: int) -> int:
    letters = ['X', 'Y', 'Z']

    starting_index = find_next_occurence(measurement_list, 0, starting_letter)
    starting_index = measurement_list.index(starting_letter)
    if starting_letter == "Z":
        ending_index = find_ending_index_of_set(
            measurement_list, starting_index, 'Y')
    distance = ending_index - starting_index

    index = ending_index + schedule_length

    while index < len(measurement_list):
        starting_index = find_next_occurence(
            measurement_list, index, starting_letter)

        if starting_index == -1:
            return distance
        else:
            ending_index = find_ending_index_of_set(
                measurement_list, starting_index, 'Y')

            distance += ending_index - starting_index

        index = ending_index + schedule_length

    return distance


def repeat_list_to_length(original_list: List, desired_length: int) -> List:
    """Repeats a list until it reaches a certain length."""
    repeated_list = (original_list * (desired_length //
                     len(original_list) + 1))[:desired_length]
    return repeated_list


def calculate_hyperedge_distance(code: GaugeHoneycombCode, rounds: int, letter: str) -> int:
    measurement_pattern = [
        edge[1].letter for edge in code.tic_tac_toe_route]

    measurement_pattern = repeat_list_to_length(
        measurement_pattern, rounds)
    return (distance_from_measurement_list(
        measurement_pattern, letter, len(code.tic_tac_toe_route)))


def test_stability_x_measurement_noise_hyper_edge_distance():
    gauge_factors = [2, 2, 2]
    for n_rounds in range(16, 30, 1):

        circuit: stim.Circuit
        circuit, code = generate_circuit(
            n_rounds, 4, gauge_factors, 'stability_x', measurement_error_probability=0.1, data_qubit_error_probability=0)

        d = calculate_hyperedge_distance(code, n_rounds, 'Z')

        check_hyper_edge_distance(
            circuit, d)


def test_stabilizer_z_measurement_noise_graphlike_distance():
    gauge_factors = [2, 2, 2]
    for n_rounds in range(18, 30, 1):
        circuit: stim.Circuit
        circuit, code = generate_circuit(
            n_rounds, 4, gauge_factors, 'stability_z', measurement_error_probability=0.1, data_qubit_error_probability=0)

        new_circuit = remove_detectors(
            circuit, [0, 1, 4, 5, 8, 9], sum(gauge_factors)*2)

        check_distance(
            new_circuit, 2*(n_rounds-7)//8+1)

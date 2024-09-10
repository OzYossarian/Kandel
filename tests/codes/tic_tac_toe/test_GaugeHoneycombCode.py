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

from main.utils.enums import State


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
#        final_measurements = [Pauli(qubit, PauliLetter(
#            'Z')) for qubit in code.data_qubits.values()]

    initial_stabilizers = [Stabilizer(
        [(0, check)], 0) for check in code.check_schedule[check_schedule_index]]

    """
    elif observable_type == 'stability_z':
        logical_observables = [code.z_stability_operator]
        check_schedule_index = 0
        final_measurements = [Pauli(qubit, PauliLetter(
            'X')) for qubit in code.data_qubits.values()]
    """

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
    print(distance)
    print(len(circuit.detector_error_model(
        approximate_disjoint_errors=True, decompose_errors=False).shortest_graphlike_error()), 'length')
    return (len(circuit.detector_error_model(
        approximate_disjoint_errors=True, decompose_errors=False).shortest_graphlike_error()))

#    assert len(circuit.detector_error_model(
 #       approximate_disjoint_errors=True).shortest_graphlike_error()) == distance


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
    return (new_circuit)


def check_hyper_edge_distance(circuit: stim.Circuit, distance):

    logical_errors = circuit.search_for_undetectable_logical_errors(
        dont_explore_detection_event_sets_with_size_above=6,
        dont_explore_edges_with_degree_above=6,
        dont_explore_edges_increasing_symptom_degree=False,
    )
    print(len(logical_errors), 'length')
#    assert len(logical_errors)a== distance


def test_stability_x_measurement_noise_graphlike_distance():
    gauge_factors = [2, 2, 2]
    distances = []

    for n_rounds in range(24, 48, 1):

        circuit: stim.Circuit
        circuit, code = generate_circuit(
            n_rounds, 4, gauge_factors, 'stability_x', measurement_error_probability=0.1, data_qubit_error_probability=0)
        new_circuit = remove_detectors(
            circuit, [2, 6, 10], sum(gauge_factors)*2)
        print(n_rounds//4 + e)
        distances.append(
            (n_rounds, check_distance(new_circuit, (n_rounds)//4)))
        # check_hyper_edge_distance(
        #  circuit, distance_of_stability(n_rounds, 'x'))

    print(distances)
test_stability_x_measurement_noise_graphlike_distance()


def test_31_rounds():
    gauge_factors = [2, 2, 2]
    n_rounds = 19

    circuit: stim.Circuit
    circuit, code = generate_circuit(
        n_rounds, 4, gauge_factors, 'stability_x', measurement_error_probability=0.1, data_qubit_error_probability=0)

    new_circuit = remove_detectors(
        circuit, [2, 6, 10], sum(gauge_factors)*2)
#    print(circuit)
    check_distance(new_circuit, (n_rounds+1)//5+1)
    # check_hyper_edge_distance(
    #   circuit, distance_of_stability(n_rounds, 'x'))


# test_31_rounds()
# test_stability_x_measurement_noise_graphlike_distance()

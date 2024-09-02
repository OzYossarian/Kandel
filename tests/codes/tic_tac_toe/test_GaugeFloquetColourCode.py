from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.gauge.GaugeFloquetColourCode import GaugeFloquetColourCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.PhenomenologicalNoise import PhenomenologicalNoise
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
import stim
import itertools
import math


def generate_circuit(rounds, distance, gauge_factors, observable_type, initial_stabilizers=None):
    code = GaugeFloquetColourCode(distance, gauge_factors)
    if observable_type == 'memory_z':
        logical_observables = [code.logical_qubits[0].z]
        check_schedule_index = gauge_factors[0]
        final_measurements = None
    elif observable_type == 'memory_x':
        logical_observables = [code.logical_qubits[1].x]
        check_schedule_index = 0
        final_measurements = None
    elif observable_type == 'stability_x':
        logical_observables = [code.x_stability_operator]
        check_schedule_index = gauge_factors[0]
        final_measurements = [Pauli(qubit, PauliLetter(
            'Z')) for qubit in code.data_qubits.values()]
    elif observable_type == 'stability_z':
        logical_observables = [code.z_stability_operator]
        check_schedule_index = 0
        final_measurements = [Pauli(qubit, PauliLetter(
            'X')) for qubit in code.data_qubits.values()]

    initial_stabilizers = [Stabilizer(
        [(0, check)], 0) for check in code.check_schedule[check_schedule_index]]

    compiler = AncillaPerCheckCompiler(
        noise_model=PhenomenologicalNoise(0.1, 0.1),
        syndrome_extractor=CxCyCzExtractor())
    stim_circuit = compiler.compile_to_stim(
        code=code,
        total_rounds=rounds,
        initial_stabilizers=initial_stabilizers,
        observables=logical_observables,
        final_measurements=final_measurements
    )
    return (stim_circuit)


def get_data_qubit_error_distance(gauge_factors, rounds):
    frequency_of_data_qubit_errors = sum(gauge_factors)
    data_qubit_error_distance = (
        rounds - (sum(gauge_factors))) / frequency_of_data_qubit_errors
    return math.ceil(data_qubit_error_distance)


def get_measurement_qubit_error_distance(gauge_factors, rounds):
    frequencies_sorted = sorted(gauge_factors)
    frequency_measurement_errors = sum(
        frequencies_sorted)/frequencies_sorted[0]
    measurement_qubit_error_distance = (
        rounds - (sum(gauge_factors))) / frequency_measurement_errors
    return math.ceil(measurement_qubit_error_distance)


def get_distance_stability_experiments(gauge_factors, rounds):
    return (min(get_data_qubit_error_distance(gauge_factors, rounds), get_measurement_qubit_error_distance(gauge_factors, rounds)))


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


def check_parity_of_number_of_violated_detectors_d4(circuit: stim.Circuit):
    assert check_for_5_detectors_violated(circuit.detector_error_model(
        approximate_disjoint_errors=True)) == True


def check_distance(circuit: stim.Circuit, distance):
    """
    logical_error = circuit.explain_detector_error_model_errors(dem_filter=(circuit.detector_error_model(
        approximate_disjoint_errors=True).shortest_graphlike_error()), reduce_to_one_representative_error=True)
    for error in logical_error:
        print(error)
    """
    print(len(circuit.detector_error_model(
        approximate_disjoint_errors=True).shortest_graphlike_error()), 'shortest error ')
    print(distance, 'distance')
    assert len(circuit.detector_error_model(
        approximate_disjoint_errors=True).shortest_graphlike_error()) == distance


def test_properties_of_d4_codes_g123():
    for gauge_factors in itertools.product([1, 2, 3], repeat=2):
        for n_rounds in range(sum(gauge_factors)*4, sum(gauge_factors)*6):
            circuit: stim.Circuit = generate_circuit(
                n_rounds, 4, gauge_factors, 'memory_z')
            check_parity_of_number_of_violated_detectors_d4(circuit)
            check_distance(circuit, 4)


def test_properties_of_d4_codes_g3456():
    circuit: stim.Circuit = generate_circuit(24, 4, [3, 4], 'memory_x')
    check_parity_of_number_of_violated_detectors_d4(circuit)
    check_distance(circuit, 4)
    circuit: stim.Circuit = generate_circuit(28, 4, [6, 1], 'memory_x')
    check_parity_of_number_of_violated_detectors_d4(circuit)
    check_distance(circuit, 4)

    circuit: stim.Circuit = generate_circuit(28, 4, [6, 3], 'memory_z')
    check_parity_of_number_of_violated_detectors_d4(circuit)
    check_distance(circuit, 4)

    circuit: stim.Circuit = generate_circuit(20, 4, [1, 5], 'memory_z')
    check_parity_of_number_of_violated_detectors_d4(circuit)
    check_distance(circuit, 4)


def test_properties_of_d4_stability():
    for rounds in range(20, 30):
        gauge_factors = [3, 2]
        circuit: stim.Circuit = generate_circuit(
            rounds, 4, gauge_factors, 'stability_x')
        with open('circuit.txt', 'w') as f:
            f.write(str(circuit))
        d = get_distance_stability_experiments(gauge_factors, rounds)
        check_distance(circuit, d)

import math
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.HoneycombCode import HoneycombCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.PhenomenologicalNoise import PhenomenologicalNoise
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
import stim

from main.utils.enums import State


def generate_circuit(rounds: int,
                     distance: int,
                     observable_type: str = 'X',
                     pauli_noise_probability: float = 0.1,
                     measurement_noise_probability: float = 0.1) -> stim.Circuit:
    """Generates a quantum error correction circuit for the Honeycomb code.

    Args:
        rounds (int): The number of rounds for the circuit.
        distance (int): The distance of the Honeycomb code.
        observable_type (str): The type of logical observable ('X' or 'Z'). Defaults to 'X'.

    Returns:
        Any: The compiled stim circuit.
    """
    code = HoneycombCode(distance)
    if observable_type == 'stability_x':
        logical_observables = [code.x_stability_operator]
        initial_stabilizers = [Stabilizer([(0, check)], 0)
                               for check in code.check_schedule[2]]
        final_measurements = code.get_possible_final_measurement(
            code.logical_qubits[1].z, rounds)
    elif observable_type == 'stability_z':
        logical_observables = [code.z_stability_operator]
        initial_stabilizers = [Stabilizer([(0, check)], 0)
                               for check in code.check_schedule[0]]
        # I just found this by drawing the detectors by hand and checking which measurements
        # create the right timelike boundary.
        final_measurements = code.get_possible_final_measurement(
            code.logical_qubits[1].x, rounds)

    elif observable_type == 'X':
        logical_observables = [code.logical_qubits[1].x]
        initial_stabilizers = [Stabilizer([(0, check)], 0)
                               for check in code.check_schedule[0]]
        final_measurements = None
    elif observable_type == 'Z':
        logical_observables = [code.logical_qubits[0].z]
        initial_stabilizers = [Stabilizer([(0, check)], 0)
                               for check in code.check_schedule[2]]
        final_measurements = None
    noise_model = PhenomenologicalNoise(
        pauli_noise_probability, measurement_noise_probability)

    compiler = AncillaPerCheckCompiler(
        noise_model=noise_model,
        syndrome_extractor=CxCyCzExtractor()
    )
    stim_circuit = compiler.compile_to_stim(
        code=code,
        total_rounds=rounds,
        initial_stabilizers=initial_stabilizers,
        observables=logical_observables,
        final_measurements=final_measurements
    )

    return stim_circuit


def check_for_5_detectors_violated(dem):
    for dem_instruction in dem:
        if dem_instruction.type == "error":
            error_targets = dem_instruction.targets_copy()
            n_violated_detectors = 0
            for target in error_targets:
                if target.is_relative_detector_id():
                    n_violated_detectors += 1
            if n_violated_detectors == 5:
                return False
    return True


def check_parity_of_number_of_violated_detectors_d4(circuit: stim.Circuit):
    assert check_for_5_detectors_violated(circuit.detector_error_model(
        approximate_disjoint_errors=True)) == True


def check_graphlike_distance(circuit: stim.Circuit, distance):
    print(len(circuit.detector_error_model(
        approximate_disjoint_errors=True, decompose_errors=False).shortest_graphlike_error()
    ))
    assert len(circuit.detector_error_model(
        approximate_disjoint_errors=True, decompose_errors=False).shortest_graphlike_error()) == distance


def check_hyper_edge_distance(circuit: stim.Circuit):

    logical_errors = circuit.search_for_undetectable_logical_errors(
        dont_explore_detection_event_sets_with_size_above=6,
        dont_explore_edges_with_degree_above=6,
        dont_explore_edges_increasing_symptom_degree=False,
    )
    for error in logical_errors:
        print(error)
    print(len(logical_errors))


def test_properties_of_d4_codes():
    for n_rounds in range(12, 24):
        circuit: stim.Circuit = generate_circuit(n_rounds, 4, 'X')
        check_parity_of_number_of_violated_detectors_d4(circuit)
        check_distance(circuit, 4)


def test_z_obs():
    circuit: stim.Circuit = generate_circuit(
        rounds=12, distance=4, observable_type='Z')
    check_parity_of_number_of_violated_detectors_d4(circuit)
    check_distance(circuit, 4)


def distance_of_stability(rounds: int, letter: str) -> int:
    if letter == 'z':
        return (math.ceil((rounds-3)/2))
    elif letter == 'x':
        return (math.ceil((rounds-2)/2))


def remove_detectors(circuit: stim.Circuit, layers_to_skip_detectors) -> stim.Circuit:
    vertical_layer = 0
    layer: stim.CircuitInstruction
    new_circuit = stim.Circuit()

    for layer in circuit:
        if layer.name == "SHIFT_COORDS":
            vertical_layer += 1

        if layer.name == "DETECTOR":
            if (vertical_layer % 6) not in layers_to_skip_detectors:
                new_circuit.append(layer)
#        elif layer.name == "OBSERVABLE_INCLUDE":
 #           if (vertical_layer % 6) not in layers_to_skip_detectors:
  #              new_circuit.append(layer)
        else:
            new_circuit.append(layer)

    return (new_circuit)


def test_stability_z():
    for n_rounds in range(12, 18):
        circuit: stim.Circuit = generate_circuit(
            rounds=n_rounds, distance=4, observable_type='stability_z',
            measurement_noise_probability=0, pauli_noise_probability=0.1)

        check_parity_of_number_of_violated_detectors_d4(circuit)
        check_graphlike_distance(circuit, distance_of_stability(n_rounds, 'z'))


def test_stability_z_measurement_noise_graphlike_distance():
    for n_rounds in range(12, 18):
        circuit: stim.Circuit = generate_circuit(
            rounds=n_rounds, distance=4, observable_type='stability_z',
            measurement_noise_probability=0.1, pauli_noise_probability=0)

        new_circuit = remove_detectors(circuit, [0, 2, 4])
        check_graphlike_distance(new_circuit, n_rounds//4)


def test_stability_x_measurement_noise_graphlike_distance():
    for n_rounds in range(12, 18):
        circuit: stim.Circuit = generate_circuit(
            rounds=n_rounds, distance=4, observable_type='stability_x',
            measurement_noise_probability=0.1, pauli_noise_probability=0)

        new_circuit = remove_detectors(circuit, [1, 3, 5])
        check_graphlike_distance(new_circuit, (n_rounds+1)//4)


def test_stability_x():
    for n_rounds in range(12, 18):
        circuit: stim.Circuit = generate_circuit(
            rounds=n_rounds, distance=4, observable_type='stability_x',
            measurement_noise_probability=0, pauli_noise_probability=0.1)

        check_parity_of_number_of_violated_detectors_d4(circuit)
        check_graphlike_distance(circuit, distance_of_stability(n_rounds, 'x'))


def test_get_final_measurement():
    code = HoneycombCode(4)
    final_measurement = code.get_possible_final_measurement(
        code.logical_qubits[1].x, 12)
    assert final_measurement == [Pauli(qubit, PauliLetter('X'))
                                 for qubit in code.data_qubits.values()]

    final_measurement = code.get_possible_final_measurement(
        code.logical_qubits[1].z, 12)
    assert final_measurement == [Pauli(qubit, PauliLetter('Y'))
                                 for qubit in code.data_qubits.values()]

import webbrowser
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.FloquetColourCode import FloquetColourCode

from main.building_blocks.detectors.Stabilizer import Stabilizer

from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.PhenomenologicalNoise import PhenomenologicalNoise
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
import stim


def generate_circuit(code, rounds, observable_type, check_schedule_index, stability_operator=None, final_measurements=None):
    if stability_operator:
        logical_observables = [stability_operator]

    elif observable_type == 'z':
        logical_observables = [code.logical_qubits[0].z]
    elif observable_type == 'x':
        logical_observables = [code.logical_qubits[1].x]

    initial_stabilizers = [Stabilizer(
        [(0, check)], 0) for check in code.check_schedule[check_schedule_index]]

    compiler = AncillaPerCheckCompiler(
        noise_model=PhenomenologicalNoise(0.1, 0.1),
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


def generate_circuit_X_observable(rounds, distance):
    code = FloquetColourCode(distance)
    return generate_circuit(code, rounds, 'x', 0)


def generate_circuit_Z_observable(rounds, distance):
    code = FloquetColourCode(distance)
    return generate_circuit(code, rounds, 'z', 1)


def generate_Z_stability_circuit(rounds, distance):
    code = FloquetColourCode(distance)
    final_measurements = [Pauli(qubit, PauliLetter(
        'X')) for qubit in code.data_qubits.values()]

    return generate_circuit(code, rounds, None, 0, stability_operator=code.z_stability_operator, final_measurements=final_measurements)


def generate_X_stability_circuit(rounds, distance):
    code = FloquetColourCode(distance)
    final_measurements = [Pauli(qubit, PauliLetter(
        'Z')) for qubit in code.data_qubits.values()]
    return generate_circuit(code, rounds, None, 1, stability_operator=code.x_stability_operator, final_measurements=final_measurements)


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
    print(len(circuit.detector_error_model(
        approximate_disjoint_errors=True).shortest_graphlike_error()))
    assert len(circuit.detector_error_model(
        approximate_disjoint_errors=True).shortest_graphlike_error()) == distance


def check_n_detectors(circuit: stim.Circuit, rounds):
    detectors_first_round = 12
    if rounds % 2 == 0:
        detectors_last_round = 8
    else:
        detectors_last_round = 16
    detectors_bulk_rounds = 4 * (rounds-3)
    assert circuit.num_detectors == detectors_first_round + \
        detectors_bulk_rounds + detectors_last_round


def test_properties_of_d4_codes():
    for n_rounds in range(12, 24):
        circuit: stim.Circuit = generate_circuit_X_observable(n_rounds, 4)
        check_parity_of_number_of_violated_detectors(circuit)
        check_n_detectors(circuit, n_rounds)
        check_distance(circuit, 4)


def test_Z_observable_d4():
    circuit: stim.Circuit = generate_circuit_Z_observable(12, 4)
    check_parity_of_number_of_violated_detectors(circuit)
    check_n_detectors(circuit, 12)
    check_distance(circuit, 4)


def test_Z_observable_d8():
    circuit: stim.Circuit = generate_circuit_Z_observable(24, 8)
    check_parity_of_number_of_violated_detectors(circuit)
    check_distance(circuit, 8)


def test_Z_stability_experiment():
    circuit: stim.Circuit = generate_Z_stability_circuit(16, 4)
    check_distance(circuit, 4)

    circuit: stim.Circuit = generate_Z_stability_circuit(12, 4)
    check_distance(circuit, 3)

    circuit: stim.Circuit = generate_Z_stability_circuit(20, 4)
    check_distance(circuit, 5)


def test_X_stability_experiment():
    circuit: stim.Circuit = generate_X_stability_circuit(16, 4)
    check_distance(circuit, 4)

    circuit: stim.Circuit = generate_X_stability_circuit(12, 4)
    check_distance(circuit, 3)

    circuit: stim.Circuit = generate_X_stability_circuit(20, 4)
    check_distance(circuit, 5)

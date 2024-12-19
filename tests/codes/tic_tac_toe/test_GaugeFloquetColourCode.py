from typing import List, Union
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.gauge.GaugeFloquetColourCode import GaugeFloquetColourCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.PhenomenologicalNoise import PhenomenologicalNoise
from main.compiling.noise.models.standard_depolarizing_noise import StandardDepolarizingNoise
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
import stim
import itertools
import pytest


def generate_circuit(gauge_factors: List[int],
                     rounds: int,
                     distance: int,
                     observable_type: str = 'X',
                     noise_model: Union[PhenomenologicalNoise,
                                        StandardDepolarizingNoise] = PhenomenologicalNoise(0.1, 0.1),
                     ) -> stim.Circuit:
    """Generates a quantum error correction circuit for the GaugeFloquetColourCode.

    Args:
        rounds (int): The number of rounds for the circuit.
        distance (int): The distance of the GaugeFloquetColourCode.
        observable_type (str): The type of logical observable ('X' or 'Z'). Defaults to 'X'.
        noise_model (Union[PhenomenologicalNoise, StandardDepolarizingNoise]): The noise model to use. Defaults to PhenomenologicalNoise(0.1, 0.1).

    Returns:
        stim.Circuit: The compiled stim circuit.
    """

    code = GaugeFloquetColourCode(distance, gauge_factors)
    if observable_type == 'memory_z':
        logical_observables = [code.logical_qubits[0].z]
        check_schedule_index = gauge_factors[0]  # TODO check
        final_measurements = None

    elif observable_type == 'memory_x':
        logical_observables = [code.logical_qubits[1].x]
        check_schedule_index = 0
        final_measurements = None

    if observable_type == 'stability_x':
        logical_observables = [code.x_stability_operator]
        check_schedule_index = gauge_factors[0]
        final_measurements = code.get_possible_final_measurement(
            code.logical_qubits[0].z, rounds)

    elif observable_type == 'stability_z':
        logical_observables = [code.z_stability_operator]
        check_schedule_index = 0
        final_measurements = code.get_possible_final_measurement(
            code.logical_qubits[1].x, rounds)

    initial_stabilizers = [Stabilizer(
        [(0, check)], 0) for check in code.check_schedule[check_schedule_index]]

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
    return stim_circuit, code


def check_for_5_detectors_violated(dem):
    # errors should only violate 1,2,3 or 4 detectors.
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


def circ_distance(circuit: stim.Circuit):
    return len(circuit.detector_error_model(
        approximate_disjoint_errors=True).shortest_graphlike_error())


def check_distance(circuit: stim.Circuit, distance):
    assert len(circuit.detector_error_model(
        approximate_disjoint_errors=True).shortest_graphlike_error()) == distance


def test_rectangular_distances():
    circuit: stim.Circuit
    circuit, _ = generate_circuit([1, 1, 1], 12, [4, 8], 'memory_x')
    check_distance(circuit, 8)

    circuit, _ = generate_circuit([1, 1, 1], 12, [8, 4],  'memory_x')
    check_distance(circuit, 4)

    circuit, _ = generate_circuit([1, 1, 1], 12, [4, 8],  'memory_z')
    check_distance(circuit, 8)

    circuit, _ = generate_circuit([1, 1, 1], 12, [8, 4],  'memory_z')
    check_distance(circuit, 4)


def test_properties_of_d4_codes_g123():
    for gauge_factors in itertools.product([1, 2, 3], repeat=2):
        for n_rounds in range(sum(gauge_factors)*4, sum(gauge_factors)*6):
            circuit, _ = generate_circuit(
                gauge_factors, n_rounds, 4, 'memory_z')
            check_parity_of_number_of_violated_detectors_d4(circuit)
            check_distance(circuit, 4)


@ pytest.mark.parametrize("rounds, distance, gauge_factors, observable_type", [
    (24, 4, [3, 4], 'memory_x'),
    (28, 4, [6, 1], 'memory_x'),
    (28, 4, [6, 3], 'memory_z'),
    (20, 4, [1, 5], 'memory_z')
])
def test_properties_of_d4_codes_g3456(rounds, distance, gauge_factors, observable_type):
    circuit, _ = generate_circuit(
        gauge_factors, rounds, distance, observable_type)
    check_parity_of_number_of_violated_detectors_d4(circuit)
    check_distance(circuit, distance)


@ pytest.mark.parametrize("gauge_factors, noise_model, observable_type", [
    ([3, 2], PhenomenologicalNoise(0, 0.1), 'stability_x'),
    ([3, 2], PhenomenologicalNoise(0, 0.1), 'stability_z'),
    ([2, 3], PhenomenologicalNoise(0.1, 0), 'stability_x'),
    ([2, 3], PhenomenologicalNoise(0.1, 0), 'stability_z')
])
def test_measurement_error_distance_varying_rounds(gauge_factors, noise_model, observable_type):
    for rounds in range(20, 30):
        circuit, code = generate_circuit(
            gauge_factors, rounds, 4, observable_type, noise_model=noise_model)
        if noise_model.measurement.p != 0:
            d = code.get_measurement_error_distance(
                rounds, observable_type.split('_')[1].upper())
        else:

            d = code.get_pauli_error_distance(
                rounds, observable_type.split('_')[1].upper())
        check_distance(circuit, d)


@ pytest.mark.parametrize("gauge_factors, rounds, observable_type, expected_distance", [
    ([1, 3], 30, 'stability_x', 4),
    ([3, 3], 30, 'stability_x', 4),
    ([2, 2], 30, 'stability_x', 4),
    ([2, 2], 20, 'stability_z', 4)
])
def test_distance_phenomenological_noise(gauge_factors, rounds, observable_type, expected_distance):
    circuit, code = generate_circuit(gauge_factors, rounds, 4, observable_type)
    d = code.get_graphlike_timelike_distance(
        rounds, observable_type.split('_')[1].upper(), 'phenomenological_noise')
    check_distance(circuit, d)


def test_get_boundary_and_bulk_layers():
    code = GaugeFloquetColourCode(4, [1, 1])
    boundary_layers, bulk_layers = code.get_boundary_and_bulk_layers(12)
    assert boundary_layers == 0
    assert bulk_layers == 0


def test_get_distance_stability_experiment():
    for r in range(12, 40):
        code = GaugeFloquetColourCode(4, [1, 1])
        d_x = code.get_non_graphlike_timelike_distance(
            r, 'Z', 'circuit_level_noise')
        circ, code = generate_circuit([1, 1], r, 4, 'stability_z',
                                      StandardDepolarizingNoise(0.1))
        print(circ_distance(circ), "DISTANCE")
        assert circ_distance(circ) == d_x


@pytest.mark.parametrize("gauge_factors", [[1, 3], [3, 1], [2, 2], [1, 1], [3, 2]])
def test_get_number_of_rounds_for_stability_experiment(gauge_factors):
    distances = [4, 5]
    for distance in distances:
        for noise_model, noise_model_str in [(PhenomenologicalNoise(0.1, 0.1), 'phenomenological_noise'),
                                             (StandardDepolarizingNoise(0.1), 'circuit_level_noise')]:
            print(noise_model_str, "noise_model")
            code = GaugeFloquetColourCode(4, gauge_factors)
            r, d_x, d_z = code.get_number_of_rounds_for_timelike_distance(
                distance, True, noise_model_str)

            circuit_x_stability, code = generate_circuit(
                gauge_factors, r, 4, 'stability_x', noise_model)

            circuit_z_stability, code = generate_circuit(
                gauge_factors, r, 4, 'stability_z', noise_model)
            check_distance(circuit_x_stability, d_x)

            check_distance(circuit_z_stability, d_z)
            assert d_x == distance or d_z == distance
            circuit, code = generate_circuit(
                gauge_factors, r-1, 4, 'stability_z', noise_model)
            z_circ_dist = circ_distance(circuit)

            circuit, code = generate_circuit(
                gauge_factors, r-1, 4, 'stability_x', noise_model)
            x_circ_dist = circ_distance(circuit)
            assert z_circ_dist < distance or x_circ_dist < distance

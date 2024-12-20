import itertools
from main.codes.tic_tac_toe.gauge.GaugeHoneycombCode import GaugeHoneycombCode
from main.codes.tic_tac_toe.gauge.GaugeFloquetColourCode import GaugeFloquetColourCode
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models import PhenomenologicalNoise
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
from matplotlib import pyplot as plt
from typing import List, Literal
import stim
import json


def generate_circuit(gauge_factors: List[int],
                     rounds: int,
                     distance: int,
                     observable_type: str = 'X',
                     pauli_noise_probability: float = 0.1,
                     measurement_noise_probability: float = 0.1) -> stim.Circuit:
    """Generates a quantum error correction circuit for the GaugeHoneycomb code.

    Args:
        rounds (int): The number of rounds for the circuit.
        distance (int): The distance of the GaugeHoneycomb code.
        observable_type (str): The type of logical observable ('X' or 'Z'). Defaults to 'X'.

    Returns:
        Any: The compiled stim circuit.
    """
    code = GaugeHoneycombCode(distance, gauge_factors)
    if observable_type == 'X':
        logical_observables = [code.x_stability_operator]

        initial_stabilizers = [Stabilizer([(0, check)], 0)
                               for check in code.check_schedule[code.gauge_factors[0] + code.gauge_factors[1]]]
        final_measurements = code.get_possible_final_measurement(
            code.logical_qubits[1].z, rounds)

    elif observable_type == 'Z':
        logical_observables = [code.z_stability_operator]
        initial_stabilizers = [Stabilizer([(0, check)], 0)
                               for check in code.check_schedule[0]]
        # I just found this by drawing the detectors by hand and checking which measurements
        # create the right timelike boundary.
        final_measurements = code.get_possible_final_measurement(
            code.logical_qubits[1].x, rounds)

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


def get_hyper_edge_distance(circuit: stim.Circuit) -> int:

    logical_errors = circuit.search_for_undetectable_logical_errors(
        dont_explore_detection_event_sets_with_size_above=4,
        dont_explore_edges_with_degree_above=4,
        dont_explore_edges_increasing_symptom_degree=False,
    )

    return len(logical_errors)


def get_td_bulk_and_boundary(gauge_factors, letter: Literal['X', 'Z']) -> int:
    bulk_length = 2*sum(gauge_factors)

    td_boundary = dict()
    for i in range(bulk_length):
        print(letter)
        circ_1 = generate_circuit(
            gauge_factors, 2*bulk_length+i, 4, letter, 0.1, 0.1)
        circ_2 = generate_circuit(
            gauge_factors, 3*bulk_length+i, 4, letter, 0.1, 0.1)
        d_1 = get_hyper_edge_distance(circ_1)

        d_2 = get_hyper_edge_distance(circ_2)
        if i == 0:
            d_1 = get_hyper_edge_distance(circ_1)
            td_bulk = d_2 - d_1
        td_boundary[i] = d_1
    return (td_bulk, td_boundary)


def generate_data():
    timelike_distance_dict = dict()
    timelike_distance_dict["X"] = dict()
    timelike_distance_dict["Z"] = dict()
    for gauge_factors in itertools.product([1, 2, 3], repeat=3):
        for letter in ["X", "Z"]:
            td_bulk, td_boundary = get_td_bulk_and_boundary(
                gauge_factors, letter)
            timelike_distance_dict[letter][str(gauge_factors)] = dict()
            timelike_distance_dict[letter][str(
                gauge_factors)]["td_bulk"] = td_bulk
            timelike_distance_dict[letter][str(
                gauge_factors)]["td_boundary"] = td_boundary
    return (timelike_distance_dict)


def main():
    timelike_distance_dict = generate_data()
    json_object = json.dumps(timelike_distance_dict, indent=4)

    # Writing to sample.json
    with open("td_data.json", "w") as outfile:
        outfile.write(json_object)


if __name__ == "__main__":
    main()

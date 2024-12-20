#!/usr/bin/env python3

import argparse
import itertools
from main.codes.tic_tac_toe.gauge.GaugeHoneycombCode import GaugeHoneycombCode
from main.codes.tic_tac_toe.gauge.GaugeFloquetColourCode import GaugeFloquetColourCode
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models import PhenomenologicalNoise
from main.compiling.noise.models.standard_depolarizing_noise import StandardDepolarizingNoise
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
from typing import List, Literal
import stim
import json


def generate_circuit(gauge_factors: List[int],
                     rounds: int,
                     distance: int,
                     observable_type: str = 'X',
                     noise_model: str = 'phenomenological',
                     code_name: str = 'GaugeHoneycombCode'
                     ) -> stim.Circuit:
    """Generates a quantum error correction circuit for the GaugeHoneycomb code.

    Args:
        rounds (int): The number of rounds for the circuit.
        distance (int): The distance of the GaugeHoneycomb code.
        observable_type (str): The type of logical observable ('X' or 'Z'). Defaults to 'X'.

    Returns:
        Any: The compiled stim circuit.
    """
    if code_name == 'GaugeHoneycombCode':
        code = GaugeHoneycombCode(distance, gauge_factors)
    elif code_name == 'GaugeFloquetColourCode':
        code = GaugeFloquetColourCode(distance, gauge_factors)
    if observable_type == 'X':
        logical_observables = [code.x_stability_operator]
        if code_name == 'GaugeHoneycombCode':
            initial_stabilizers = [Stabilizer([(0, check)], 0)
                                   for check in code.check_schedule[code.gauge_factors[0] + code.gauge_factors[1]]]
        elif code_name == 'GaugeFloquetColourCode':
            initial_stabilizers = [Stabilizer([(0, check)], 0)
                                   for check in code.check_schedule[code.gauge_factors[0]]]

        final_measurements = code.get_possible_final_measurement(
            code.logical_qubits[1].z, rounds)

    elif observable_type == 'Z':
        logical_observables = [code.z_stability_operator]
        initial_stabilizers = [Stabilizer([(0, check)], 0)
                               for check in code.check_schedule[0]]
        final_measurements = code.get_possible_final_measurement(
            code.logical_qubits[1].x, rounds)

    if noise_model == 'phenomenological':
        noise_model = PhenomenologicalNoise(
            0.1, 0.1)
    elif noise_model == 'circuit_level_depolarizing':

        noise_model = StandardDepolarizingNoise(
            0.1)

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


def get_graphlike_distance(circuit: stim.Circuit) -> int:
    return len(circuit.detector_error_model(decompose_errors=True, approximate_disjoint_errors=True).shortest_graphlike_error())


def get_td_bulk_and_boundary(noise_model, gauge_factors, bulk_length, letter: Literal['X', 'Z'], graphlike) -> int:
    td_boundary = dict()

    for i in range(bulk_length):

        circ_1 = generate_circuit(

            gauge_factors, bulk_length+i, 4, letter, noise_model, "GaugeFloquetColourCode")

        circ_2 = generate_circuit(
            gauge_factors, 2*bulk_length+i, 4, letter, noise_model,  "GaugeFloquetColourCode")

        if graphlike == True:
            d_1 = get_graphlike_distance(circ_1)
            d_2 = get_graphlike_distance(circ_2)
        else:
            d_1 = get_hyper_edge_distance(circ_1)
            d_2 = get_hyper_edge_distance(circ_2)

        if i == 0:
            td_bulk = d_2 - d_1
        td_boundary[i] = d_1

    return (td_bulk, td_boundary)


def get_hyper_edge_distance(circuit: stim.Circuit) -> int:
    logical_errors = circuit.search_for_undetectable_logical_errors(
        dont_explore_detection_event_sets_with_size_above=8,
        dont_explore_edges_with_degree_above=8,
        dont_explore_edges_increasing_symptom_degree=False,
        canonicalize_circuit_errors=True
    )

    return len(logical_errors)


def generate_data(noise_model, code, graphlike=True):
    timelike_distance_dict = dict()
    timelike_distance_dict["X"] = dict()
    timelike_distance_dict["Z"] = dict()
    if code == 'GaugeHoneycombCode':
        gauge_factor_combinations = itertools.product([1, 2, 3], repeat=3)
    elif code == 'GaugeFloquetColourCode':
        gauge_factor_combinations = itertools.product([1, 2, 3], repeat=2)
    for gauge_factors in gauge_factor_combinations:
        for letter in ["X", "Z"]:
            if code == "GaugeFloquetColourCode":

                bulk_length = 6*(gauge_factors[0] + gauge_factors[1])
            elif code == "GaugeHoneycombCode":
                bulk_length = 4 * \
                    (gauge_factors[0] + gauge_factors[1] + gauge_factors[2])
            td_bulk, td_boundary = get_td_bulk_and_boundary(noise_model,
                                                            gauge_factors,
                                                            bulk_length,
                                                            letter,
                                                            graphlike)

            timelike_distance_dict[letter][str(gauge_factors)] = dict()
            timelike_distance_dict[letter][str(
                gauge_factors)]["td_bulk"] = td_bulk
            timelike_distance_dict[letter][str(
                gauge_factors)]["td_boundary"] = td_boundary
    return (timelike_distance_dict)


def main(code, noise_model, graphlike):
    timelike_distance_dict = generate_data(
        noise_model, code, graphlike)
    json_object = json.dumps(timelike_distance_dict, indent=4)
    file_prefix = "fcc" if code == "GaugeFloquetColourCode" else "hcc"
    with open(f"./timelike_distance_data/{file_prefix}_{'graphlike' if graphlike else 'non_graphlike'}_td_data_{noise_model}.json", "w") as outfile:
        outfile.write(json_object)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', type=str, required=True)
    parser.add_argument('--noise_model', type=str, required=True)
    parser.add_argument('--graphlike', type=int, required=True)
    args = parser.parse_args()
    main(
        args.code,
        args.noise_model,
        bool(args.graphlike)
    )

from main.codes.tic_tac_toe.FloquetColourCode import FloquetColourCode

from main.building_blocks.detectors.Stabilizer import Stabilizer

from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.PhenomenologicalNoise import PhenomenologicalNoise
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
import stim


def generate_circuit(rounds, distance):
    code = FloquetColourCode(distance)
    logical_observables = [code.logical_qubits[1].x]
    initial_stabilizers = []
    for check in code.check_schedule[0]:
        initial_stabilizers.append(Stabilizer([(0, check)], 0))

    compiler = AncillaPerCheckCompiler(
        noise_model=PhenomenologicalNoise(1, 1),
        syndrome_extractor=CxCyCzExtractor())
    stim_circuit = compiler.compile_to_stim(
        code=code,
        total_rounds=rounds,
        initial_stabilizers=initial_stabilizers,
        observables=logical_observables
    )
    return (stim_circuit)


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
        circuit: stim.Circuit = generate_circuit(n_rounds, 4)
        check_parity_of_number_of_violated_detectors(circuit)
        check_n_detectors(circuit, n_rounds)
        check_distance(circuit, 4)

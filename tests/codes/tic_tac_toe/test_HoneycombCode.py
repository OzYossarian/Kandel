from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.codes.tic_tac_toe.HoneycombCode import HoneycombCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.PhenomenologicalNoise import PhenomenologicalNoise
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
import stim

from main.utils.enums import State


def generate_circuit(rounds, distance):
    code = HoneycombCode(distance)
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


def generate_circuit_Z_observable(rounds, distance):

    code = HoneycombCode(distance)
    logical_observables = [code.logical_qubits[0].z]
    initial_states = dict()
    for qubit in code.data_qubits.values():

        #        check = Check([Pauli(qubit, letter=PauliLetter("Z"))])
        initial_states[qubit] = State(0)
#        initial_stabilizers.append(Stabilizer([(0, check)], 0))
#    for check in code.check_schedule[gauge_factors[0]+gauge_factors[1]]:
#           initial_stabilizers.append(Stabilizer([(0, check)], 0))

    compiler = AncillaPerCheckCompiler(
        noise_model=PhenomenologicalNoise(0.1, 0.1),
        syndrome_extractor=CxCyCzExtractor())
    stim_circuit = compiler.compile_to_stim(
        code=code,
        total_rounds=rounds,
        initial_states=initial_states,
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


def check_parity_of_number_of_violated_detectors_d4(circuit: stim.Circuit):
    assert check_for_5_detectors_violated(circuit.detector_error_model(
        approximate_disjoint_errors=True)) == True


def check_distance(circuit: stim.Circuit, distance):
    assert len(circuit.detector_error_model(
        approximate_disjoint_errors=True).shortest_graphlike_error()) == distance


def test_properties_of_d4_codes():
    for n_rounds in range(12, 24):

        circuit: stim.Circuit = generate_circuit(n_rounds, 4)
        check_parity_of_number_of_violated_detectors_d4(circuit)
        check_distance(circuit, 4)


def test_z_obs():
    circuit: stim.Circuit = generate_circuit_Z_observable(12, 4)
    print(circuit)
    check_parity_of_number_of_violated_detectors_d4(circuit)
    check_distance(circuit, 4)


test_z_obs()

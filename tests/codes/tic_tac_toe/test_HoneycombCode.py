from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.codes.tic_tac_toe.HoneycombCode import HoneycombCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.PhenomenologicalNoise import PhenomenologicalNoise
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
import stim

from main.utils.enums import State


def generate_circuit(rounds: int, distance: int, observable_type: str = 'X') -> stim.Circuit:
    """Generates a quantum error correction circuit for the Honeycomb code.

    Args:
        rounds (int): The number of rounds for the circuit.
        distance (int): The distance of the Honeycomb code.
        observable_type (str): The type of logical observable ('X' or 'Z'). Defaults to 'X'.

    Returns:
        Any: The compiled stim circuit.
    """
    code = HoneycombCode(distance)

    if observable_type == 'X':
        logical_observables = [code.logical_qubits[1].x]
        initial_stabilizers = [Stabilizer([(0, check)], 0)
                               for check in code.check_schedule[0]]
        initial_states = None
        noise_model = PhenomenologicalNoise(1, 1)
    elif observable_type == 'Z':
        logical_observables = [code.logical_qubits[0].z]
        initial_stabilizers = []
        initial_states = {qubit: State(0)
                          for qubit in code.data_qubits.values()}
        noise_model = PhenomenologicalNoise(0.1, 0.1)
    else:
        raise ValueError("observable_type must be 'X' or 'Z'")

    compiler = AncillaPerCheckCompiler(
        noise_model=noise_model,
        syndrome_extractor=CxCyCzExtractor()
    )

    stim_circuit = compiler.compile_to_stim(
        code=code,
        total_rounds=rounds,
        initial_stabilizers=initial_stabilizers,
        initial_states=initial_states,
        observables=logical_observables
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


def check_distance(circuit: stim.Circuit, distance):
    assert len(circuit.detector_error_model(
        approximate_disjoint_errors=True).shortest_graphlike_error()) == distance


def test_properties_of_d4_codes():
    for n_rounds in range(12, 24):
        circuit: stim.Circuit = generate_circuit(n_rounds, 4, 'X')
        check_parity_of_number_of_violated_detectors_d4(circuit)
        check_distance(circuit, 4)


def test_z_obs():
    circuit: stim.Circuit = generate_circuit(
        n_rounds=12, distance=4, observable_type='Z')
    check_parity_of_number_of_violated_detectors_d4(circuit)
    check_distance(circuit, 4)

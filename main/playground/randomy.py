from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.utils import plus_one_eigenstates
from main.codes.hexagonal.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.codes.hexagonal.tic_tac_toe.utils import random_good_route
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.PhenomenologicalNoise import PhenomenologicalNoise
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import TrivialOrderer
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed import CxCyCzExtractor

distance = 4
pseudo_layer_size = 3
route = random_good_route(distance * pseudo_layer_size)
code = TicTacToeCode(distance, route)

noise_model = PhenomenologicalNoise(0.1, 0.2)
extractor = CxCyCzExtractor(TrivialOrderer())
compiler = AncillaPerCheckCompiler(noise_model, extractor)

initial_checks_letter = code.tic_tac_toe_route[0][1]
initial_state = plus_one_eigenstates[initial_checks_letter]
data_qubits = code.data_qubits.values()
initial_states = {
    qubit: initial_state for qubit in data_qubits}
final_measurements = [
    Pauli(qubit, initial_checks_letter) for qubit in data_qubits]
# TODO - a very curious bug. Using logical X_0 as the observable leads to a
#  non-deterministic observable being found some of the time. Hasn't happened
#  yet for logical X_1, strangely.
observables = [code.logical_qubits[1].x]
circuit = compiler.compile_code(
    code=code,
    layers=1,
    initial_states=initial_states,
    final_measurements=final_measurements,
    logical_observables=observables)

print(circuit)
dem = circuit.detector_error_model(
    approximate_disjoint_errors=True)

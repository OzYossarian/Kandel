from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.codes.tic_tac_toe.FloquetColourCode import FloquetColourCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.CodeCapacityBitFlipNoise import (
    CodeCapacityBitFlipNoise,
)
from main.compiling.noise.models.NoNoise import NoNoise
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import (
    CxCyCzExtractor,
)
from main.utils.Colour import Blue, Green, Red
from main.utils.enums import State
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
import stim

"""
code = FloquetColourCode(4)
compiler = AncillaPerCheckCompiler(noise_model=CodeCapacityBitFlipNoise(0.1), syndrome_extractor=CxCyCzExtractor())
data_qubits = code.data_qubits.values()
data_qubit_initial_states = {qubit: State.Plus for qubit in data_qubits}
final_measurements = [Pauli(qubit, PauliLetter('X')) for qubit in data_qubits]
logical_observables = [code.logical_qubits[1].x]


#for i in range(-1,3):
#    print(i)
#    print([pauli.qubit.coords for pauli in code.logical_qubits[0].x.at_round(i)])   
#    print([pauli.letter for pauli in code.logical_qubits[0].x.at_round(i)])


stim_circuit: stim.Circuit = compiler.compile_to_stim(code,layers=1, 
                                                      initial_states= data_qubit_initial_states, 
                                                      final_measurements=final_measurements,
                                                      logical_observables=logical_observables)

#print(stim_circuit)
#print(stim_circuit.detector_error_model(approximate_disjoint_errors=True))
#print(stim_circuit.num_detectors)
#"""


def test_stability_experiment():
    code = FloquetColourCode(4)
    compiler = AncillaPerCheckCompiler(
        noise_model=NoNoise(), syndrome_extractor=CxCyCzExtractor()
    )
    compiler.add_ancilla_qubits(code)
    data_qubits = code.data_qubits.values()
    final_measurements = [Pauli(qubit, PauliLetter("X")) for qubit in data_qubits]

    initial_stabilizers = []
    for check in code.check_schedule[0]:
        initial_stabilizers.append(Stabilizer([(0, check)], 0))

    # o
    stim_circuit: stim.Circuit = compiler.compile_to_stim(
        code,
        layers=4,
        final_measurements=final_measurements,
        initial_stabilizers=initial_stabilizers,
        stability_observable_rounds=[1, 3],
        stability=True,
    )
    print(stim_circuit)
    stim_circuit.detector_error_model(approximate_disjoint_errors=True)


test_stability_experiment()

from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ, PauliX
from main.codes.RepetitionCode import RepetitionCode
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.codes.hexagonal.tic_tac_toe.FloquetColourCode import FloquetColourCode
from main.codes.hexagonal.tic_tac_toe.HoneycombCode import HoneycombCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.CircuitLevelNoise import CircuitLevelNoise
from main.compiling.noise.models.CodeCapacityBitFlipNoise import CodeCapacityBitFlipNoise
from main.compiling.noise.models.NoNoise import NoNoise
from main.compiling.noise.models.PhenomenologicalNoise import PhenomenologicalNoise
from main.compiling.syndrome_extraction.controlled_gate_orderers.RotatedSurfaceCodeOrderer import RotatedSurfaceCodeOrderer
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import TrivialOrderer
from main.compiling.syndrome_extraction.extractors.mixed.CxCyCzExtractor import CxCyCzExtractor
from main.compiling.syndrome_extraction.extractors.pure.PurePauliWordExtractor import PurePauliWordExtractor
from main.compiling.syndrome_extraction.extractors.mixed.UniformAncillaBasisExtractor import UniformAncillaBasisExtractor
from main.enums import State
from main.printing.Printer2D import Printer2D


# Codes
rep_code = RepetitionCode(3)
rsc = RotatedSurfaceCode(3)
fcc = FloquetColourCode(4)
hcc = HoneycombCode(4)

# Print codes
printer = Printer2D()

# Orderers
trivial_orderer = TrivialOrderer()
rsc_orderer = RotatedSurfaceCodeOrderer()

# Extractors
trivial_extractor = CxCyCzExtractor(trivial_orderer)
rsc_extractor = CxCyCzExtractor(rsc_orderer)

# Noise models
phenom_noise = PhenomenologicalNoise(0.1, 0.1)
circuit_level_noise = CircuitLevelNoise(0.1, 0.2, 0.3, 0.4, 0.5)
code_capacity_noise = CodeCapacityBitFlipNoise(0.2)
no_noise = NoNoise()

# Compilers
noiseless_trivial_compiler = AncillaPerCheckCompiler(no_noise, trivial_extractor)
phenom_trivial_compiler = AncillaPerCheckCompiler(phenom_noise, trivial_extractor)
cln_trivial_compiler = AncillaPerCheckCompiler(circuit_level_noise, trivial_extractor)
phenom_rsc_compiler = AncillaPerCheckCompiler(phenom_noise, rsc_extractor)
capacity_rsc_compiler = AncillaPerCheckCompiler(code_capacity_noise, rsc_extractor)

# Circuits
fcc_qubits = list(fcc.data_qubits.values())
fcc_initials = {qubit: State.Plus for qubit in fcc_qubits}
fcc_finals = [Pauli(qubit, PauliX) for qubit in fcc_qubits]
fcc_logicals = [fcc.logical_qubits[1].x]
phenom_fcc_circuit = phenom_trivial_compiler.compile_code(
    fcc, 2,
    initial_states=fcc_initials,
    final_measurements=fcc_finals,
    logical_observables=fcc_logicals)

hcc_qubits = list(hcc.data_qubits.values())
hcc_initials = {qubit: State.Plus for qubit in hcc_qubits}
hcc_finals = [Pauli(qubit, PauliX) for qubit in hcc_qubits]
hcc_logicals = [hcc.logical_qubits[0].x]
phenom_hcc_circuit = phenom_trivial_compiler.compile_code(
    hcc, hcc.distance,
    initial_states=hcc_initials,
    final_measurements=hcc_finals,
    logical_observables=hcc_logicals)

# cProfile.run(
#      'phenom_pure_trivial_compiler.compile_code('
#      'hcc, hcc.distance, hcc_initials, hcc_finals, hcc_logicals)',
#      'hcc_distance_16_better_determinism_checks.prof')

rsc_qubits = list(rsc.data_qubits.values())
rsc_initials = {qubit: State.Zero for qubit in rsc_qubits}
rsc_finals = [Pauli(qubit, PauliZ) for qubit in rsc_qubits]
rsc_logicals = [rsc.logical_qubits[0].z]
phenom_rsc_circuit = phenom_rsc_compiler.compile_code(
    rsc, rsc.distance,
    initial_states=rsc_initials,
    final_measurements=rsc_finals,
    logical_observables=rsc_logicals)

# cProfile.run(
#      'phenom_pure_rsc_compiler.compile_code(rsc, rsc.distance, rsc_initials, rsc_finals, rsc_logicals)',
#      f'rsc_distance_{rsc.distance}.prof')
#
rep_qubits = list(rep_code.data_qubits.values())
rep_initials = {qubit: State.Zero for qubit in rep_qubits}
rep_finals = [Pauli(qubit, PauliZ) for qubit in rep_qubits]
rep_logicals = [rep_code.logical_qubits[0].z]
phenom_rep_circuit = phenom_trivial_compiler.compile_code(
    rep_code, rep_code.distance,
    initial_states=rep_initials,
    final_measurements=rep_finals,
    logical_observables=rep_logicals)

# Printing
print(phenom_rep_circuit)
# print()
# print(phenom_rsc_circuit)
# print()
# print(phenom_fcc_circuit)
# print()
# print(phenom_hcc_circuit)

# Raw sampling
# raw_sampler = noiseless_pure_fcc_circuit.compile_sampler()
# print(raw_sampler.sample(shots=1))

# Detector sampling
# fcc_detector_sampler = noiseless_pure_fcc_circuit.compile_detector_sampler()
# print(fcc_detector_sampler.sample(shots=1))

# # Detector error models
# model = phenom_fcc_circuit.detector_error_model(
#     approximate_disjoint_errors=True)
# model = phenom_hcc_circuit.detector_error_model(
#     approximate_disjoint_errors=True)
# print(model)

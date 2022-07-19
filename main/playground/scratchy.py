import cProfile

from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ, PauliX
from main.codes.RepetitionCode import RepetitionCode
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.codes.hexagonal.TriangularColourCode import TriangularColourCode
from main.codes.hexagonal.tic_tac_toe.FloquetColourCode import FloquetColourCode
from main.codes.hexagonal.tic_tac_toe.HoneycombCode import HoneycombCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.CircuitLevelNoise import CircuitLevelNoise
from main.compiling.noise.models.CodeCapacityBitFlipNoise import CodeCapacityBitFlipNoise
from main.compiling.noise.models.NoNoise import NoNoise
from main.compiling.noise.models.PhenomenologicalNoise import PhenomenologicalNoise
from main.compiling.syndrome_extraction.controlled_gate_orderers.RotatedSurfaceCodeOrderer import RotatedSurfaceCodeOrderer
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import TrivialOrderer
from main.compiling.syndrome_extraction.extractors.PurePauliWordExtractor import PurePauliWordExtractor
from main.compiling.syndrome_extraction.extractors.SyndromeExtractor import SyndromeExtractor
from main.enums import State
from main.printing.Printer2D import Printer2D


# Codes
# rep_code = RepetitionCode(3)
rsc = RotatedSurfaceCode(15)
# fcc = FloquetColourCode(4)
hcc = HoneycombCode(16)

# Orderers
trivial_orderer = TrivialOrderer()
rsc_orderer = RotatedSurfaceCodeOrderer()

# Extractors
mixed_trivial_extractor = SyndromeExtractor(trivial_orderer)
pure_trivial_extractor = PurePauliWordExtractor(trivial_orderer)
rsc_extractor = SyndromeExtractor(rsc_orderer)
pure_rsc_extractor = PurePauliWordExtractor(rsc_orderer)

# Noise models
phenom_noise = PhenomenologicalNoise(0.1, 0.1)
circuit_level_noise = CircuitLevelNoise(0.1, 0.2, 0.3, 0.4, 0.5)
code_capacity_noise = CodeCapacityBitFlipNoise(0.2)
no_noise = NoNoise()

# Compilers
noiseless_mixed_trivial_compiler = AncillaPerCheckCompiler(no_noise, mixed_trivial_extractor)
noiseless_pure_trivial_compiler = AncillaPerCheckCompiler(no_noise, pure_trivial_extractor)
phenom_mixed_trivial_compiler = AncillaPerCheckCompiler(phenom_noise, mixed_trivial_extractor)
phenom_pure_trivial_compiler = AncillaPerCheckCompiler(phenom_noise, pure_trivial_extractor)
cln_mixed_trivial_compiler = AncillaPerCheckCompiler(circuit_level_noise, mixed_trivial_extractor)
phenom_rsc_compiler = AncillaPerCheckCompiler(phenom_noise, rsc_extractor)
phenom_pure_rsc_compiler = AncillaPerCheckCompiler(phenom_noise, pure_rsc_extractor)
capacity_pure_rsc_compiler = AncillaPerCheckCompiler(code_capacity_noise, pure_rsc_extractor)

# Circuits
# cln_mixed_rep_circuit = cln_mixed_trivial_compiler.compile_code(rep_code, 5)
# noiseless_pure_fcc_circuit = noiseless_pure_trivial_compiler.compile_code(fcc, 2)

# fcc_qubits = list(fcc.data_qubits.values())
# fcc_initials = {qubit: State.Plus for qubit in fcc_qubits}
# fcc_finals = [Pauli(qubit, PauliX) for qubit in fcc_qubits]
# fcc_logicals = [fcc.logical_qubits[1].x]
# phenom_fcc_circuit = phenom_pure_trivial_compiler.compile_code(
#     fcc, 2, fcc_initials, fcc_finals, fcc_logicals)

# hcc_qubits = list(hcc.data_qubits.values())
# hcc_initials = {qubit: State.Plus for qubit in hcc_qubits}
# hcc_finals = [Pauli(qubit, PauliX) for qubit in hcc_qubits]
# hcc_logicals = [hcc.logical_qubits[0].x]
# cProfile.run(
#      'phenom_pure_trivial_compiler.compile_code('
#      'hcc, hcc.distance, hcc_initials, hcc_finals, hcc_logicals)',
#      'hcc_distance_16_better_determinism_checks.prof')
# phenom_hcc_circuit = phenom_pure_trivial_compiler.compile_code(
#     hcc, hcc.distance, hcc_initials, hcc_finals, hcc_logicals)

rsc_qubits = list(rsc.data_qubits.values())
rsc_initials = {qubit: State.Zero for qubit in rsc_qubits}
rsc_finals = [Pauli(qubit, PauliZ) for qubit in rsc_qubits]
rsc_logicals = [rsc.logical_qubits[0].z]
phenom_rsc_circuit = phenom_pure_rsc_compiler.compile_code(
     rsc, rsc.distance, rsc_initials, rsc_finals, rsc_logicals)
# cProfile.run(
#      'phenom_pure_rsc_compiler.compile_code(rsc, rsc.distance, rsc_initials, rsc_finals, rsc_logicals)',
#      f'rsc_distance_{rsc.distance}.prof')
#
# rep_qubits = list(rep_code.data_qubits.values())
# rep_initials = {qubit: State.Zero for qubit in rep_qubits}
# rep_finals = [Pauli(qubit, PauliZ) for qubit in rep_qubits]
# rep_logicals = [rep_code.logical_qubits[0].z]
# phenom_rep_circuit = phenom_pure_trivial_compiler.compile_code(
#     rep_code, 2, rep_initials, rep_finals, rep_logicals)

# Printing
# print(phenom_rep_circuit)
# print()
print(phenom_rsc_circuit)
# print()
# print(capacity_rsc_circuit)
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

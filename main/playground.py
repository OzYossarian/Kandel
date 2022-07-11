from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ
from main.codes.RepetitionCode import RepetitionCode
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.codes.hexagonal.TriangularColourCode import TriangularColourCode
from main.codes.hexagonal.tic_tac_toe.FloquetColourCode import FloquetColourCode
from main.codes.hexagonal.tic_tac_toe.HoneycombCode import HoneycombCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.CircuitLevelNoise import CircuitLevelNoise
from main.compiling.noise.models.NoNoise import NoNoise
from main.compiling.noise.models.PhenomenologicalNoise import PhenomenologicalNoise
from main.compiling.syndrome_extraction.controlled_gate_orderers.RotatedSurfaceCodeOrderer import RotatedSurfaceCodeOrderer
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import TrivialOrderer
from main.compiling.syndrome_extraction.extractors.PurePauliWordExtractor import PurePauliWordExtractor
from main.compiling.syndrome_extraction.extractors.SyndromeExtractor import SyndromeExtractor
from main.enums import State
from main.printing.Printer2D import Printer2D


# Codes
rep_code = RepetitionCode(3)
rsc = RotatedSurfaceCode(3)
fcc = FloquetColourCode(4)
hcc = HoneycombCode(4)

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
no_noise = NoNoise()

# Compilers
noiseless_mixed_trivial_compiler = AncillaPerCheckCompiler(no_noise, mixed_trivial_extractor)
noiseless_pure_trivial_compiler = AncillaPerCheckCompiler(no_noise, pure_trivial_extractor)
phenom_mixed_trivial_compiler = AncillaPerCheckCompiler(phenom_noise, mixed_trivial_extractor)
phenom_pure_trivial_compiler = AncillaPerCheckCompiler(phenom_noise, pure_trivial_extractor)
cln_mixed_trivial_compiler = AncillaPerCheckCompiler(circuit_level_noise, mixed_trivial_extractor)
phenom_rsc_compiler = AncillaPerCheckCompiler(phenom_noise, rsc_extractor)
phenom_pure_rsc_compiler = AncillaPerCheckCompiler(phenom_noise, pure_rsc_extractor)

# Circuits
# cln_mixed_rep_circuit = cln_mixed_trivial_compiler.compile_code(rep_code, 5)
# noiseless_pure_fcc_circuit = noiseless_pure_trivial_compiler.compile_code(fcc, 2)

fcc_qubits = list(fcc.data_qubits.values())
fcc_initials = {qubit: State.Zero for qubit in fcc_qubits}
fcc_finals = [Pauli(qubit, PauliZ) for qubit in fcc_qubits]
fcc_logicals = [fcc.logical_qubits[0].z]
# [print(pauli) for pauli in fcc.logical_qubits[0].z.paulis]
# [print(fcc.get_logical_qubit_types(i-1)) for i in range(12)]
phenom_fcc_circuit = phenom_pure_trivial_compiler.compile_code(
    fcc, 2, fcc_initials, fcc_finals, fcc_logicals)

# rsc_qubits = list(rsc.data_qubits.values())
# rsc_initials = {qubit: State.Zero for qubit in rsc_qubits}
# rsc_finals = [Pauli(qubit, PauliZ) for qubit in rsc_qubits]
# rsc_logicals = [rsc.logical_qubits[0].z]
# phenom_rsc_circuit = phenom_pure_rsc_compiler.compile_code(
#     rsc, 2, rsc_initials, rsc_finals, rsc_logicals)
#
# rep_qubits = list(rep_code.data_qubits.values())
# rep_initials = {qubit: State.Zero for qubit in rep_qubits}
# rep_finals = [Pauli(qubit, PauliZ) for qubit in rep_qubits]
# rep_logicals = [rep_code.logical_qubits[0].z]
# phenom_rep_circuit = phenom_pure_trivial_compiler.compile_code(
#     rep_code, 2, rep_initials, rep_finals, rep_logicals)

# Printing
# print(phenom_rep_circuit)
# print(phenom_rsc_circuit)
print(phenom_fcc_circuit)
# print(phenom_hcc_circuit)

# Raw sampling
# raw_sampler = noiseless_pure_fcc_circuit.compile_sampler()
# print(raw_sampler.sample(shots=1))

# Detector sampling
# fcc_detector_sampler = noiseless_pure_fcc_circuit.compile_detector_sampler()
# print(fcc_detector_sampler.sample(shots=1))

# Detector error models
# model = phenom_rsc_circuit.detector_error_model(
#     approximate_disjoint_errors=True)
# print(repr(model))

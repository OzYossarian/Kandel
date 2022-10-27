from py import code
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.RepetitionCode import RepetitionCode
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.CodeCapacityBitFlipNoise import CodeCapacityBitFlipNoise
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import TrivialOrderer
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed import CxCyCzExtractor
from main.decoding.PymatchingDecoder import PymatchingDecoder
import numpy as np

from main.utils.enums import State


class IdlingExperiment():
    def __init__(self, code_name, distance, noise_model):
        self.distance = distance
        self.noise_model = noise_model
        code_dict = {
            'RotatedSurfaceCode': RotatedSurfaceCode, 
            'RepetitionCode': RepetitionCode}
        self.code = code_dict[code_name](self.distance)
        self.stim_circuit, self.decoder, self.sampler = \
            self.initialize_circuit(noise_model)

    def initialize_circuit(self, noise_model, decoder='pymatching'):
        pure_trivial_extractor = CxCyCzExtractor(TrivialOrderer())
        compiler = AncillaPerCheckCompiler(noise_model, pure_trivial_extractor)

        code_qubits = list(self.code.data_qubits.values())
    
        code_initials = {qubit: State.Zero for qubit in code_qubits}
        code_finals = [Pauli(qubit, PauliLetter('Z')) for qubit in code_qubits]
        code_logicals = [self.code.logical_qubits[0].z]

        if noise_model.measurement is None:
            circuit = compiler.compile_code(
                code=self.code,
                layers=1,
                initial_states=code_initials,
                final_measurements=code_finals,
                logical_observables=code_logicals)
        else:
            circuit = compiler.compile_code(
                code, 3)
        decoder = PymatchingDecoder(
            circuit.detector_error_model(decompose_errors=True, approximate_disjoint_errors = True))
        sampler = circuit.compile_detector_sampler()
        return (circuit, decoder, sampler)

    def calculate_ler(self, n_runs):
        shots = self.sampler.sample(shots=n_runs, append_observables=True)
        detector_parts = shots[:, :self.stim_circuit.num_detectors]
        actual_observable_parts = shots[:, self.stim_circuit.num_detectors:]
        predicted_observable_parts = self.decoder.decode_samples(
            detector_parts)
        num_errors = 0
        for actual, predicted in zip(actual_observable_parts, predicted_observable_parts):
            if not np.array_equal(actual, predicted):
                num_errors += 1
        return num_errors/n_runs


if __name__ == "__main__":
    noise_model = CodeCapacityBitFlipNoise(0.2)
    exp = IdlingExperiment('RotatedSurfaceCode', 3, noise_model)
    num_errors = exp.calculate_ler(1000)
    print(num_errors)

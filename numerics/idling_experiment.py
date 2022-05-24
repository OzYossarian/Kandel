from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.compiling.compilers.Compiler import Compiler
from main.compiling.noise.models.CodeCapacityBitFlipNoise import CodeCapacityBitFlipNoise
from main.compiling.syndrome_extraction.controlled_gate_orderers.RotatedSurfaceCodeOrderer import RotatedSurfaceCodeOrderer
from main.compiling.syndrome_extraction.extractors.CSSExtractor import PurePauliWordExtractor
from main.decoding.PymatchingDecoder import PymatchingDecoder
import numpy as np


class IdlingExperiment():
    def __init__(self, code_name, distance, noise_model):
        self.distance = distance
        self.noise_model = noise_model
        code_dict = {
            'RotatedSurfaceCode': RotatedSurfaceCode}
        self.code = code_dict[code_name](self.distance)
        self.stim_circuit, self.decoder, self.sampler = \
            self.initialize_circuit(noise_model)

    def initialize_circuit(self, noise_model, decoder='pymatching'):
        syndrome_extractor = PurePauliWordExtractor(RotatedSurfaceCodeOrderer())
        compiler = Compiler(noise_model, syndrome_extractor)
        stim_circuit = compiler.compile_code(
            self.code, layers=self.distance, perfect_final_layer=True)
        print(stim_circuit)

        decoder = PymatchingDecoder(
            stim_circuit.detector_error_model(decompose_errors=True, approximate_disjoint_errors=True))
        print(stim_circuit.detector_error_model())

        sampler = stim_circuit.compile_detector_sampler()
        print(decoder.matcher.matching_graph)

        return stim_circuit, decoder, sampler

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

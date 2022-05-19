from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.compiling.Circuit import Circuit
from main.compiling.NoiseModel import NoiseModel, CodeCapactiyBitFlipNoise, PhenomenologicalNoise
from main.compiling.Compiler import Compiler
from main.decoding.PymatchingDecoder import PymatchingDecoder
import numpy as np


class IdlingExperiment():
    def __init__(self, code_name, distance, noise_model):
        self.distance = distance
        self.initialize_code(code_name)
        self.initialize_circuit(noise_model)

    def initialize_code(self, code_name):
        code_dict = {'RotatedSurfaceCode': RotatedSurfaceCode}
        if code_name in code_dict:
            self.code = code_dict[code_name](self.distance)

    def initialize_circuit(self, noise_model, decoder='pymatching'):
        compiler = Compiler(noise_model)
        circuit = Circuit()

        if noise_model.ancilla_qubit_MZ == 0:
            compiler.compile_code(
                self.code, repeat_block=False, final_block=False, measure_data_qubits=True)
            circuit.to_stim(compiler.gates_at_timesteps,
                            compiler.detector_qubits)
        else:
            compiler.compile_code(
                self.code, repeat_block=True, final_block=True, measure_data_qubits=True)
            circuit.to_stim(compiler.gates_at_timesteps,
                            compiler.detector_qubits, n_code_rounds=self.distance)
        self.circuit = circuit.full_circuit
        self.decoder = PymatchingDecoder(
            self.circuit.detector_error_model(decompose_errors=True))
        print(self.circuit.detector_error_model())
        self.sampler = self.circuit.compile_detector_sampler()
        print(self.decoder.matcher.matching_graph)

    def calculate_ler(self, n_runs):

        shots = self.sampler.sample(shots=n_runs, append_observables=True)
        detector_parts = shots[:, :self.circuit.num_detectors]
        actual_observable_parts = shots[:, self.circuit.num_detectors:]
        predicted_observable_parts = self.decoder.decode_samples(
            detector_parts)

        num_errors = 0

        for actual, predicted in zip(actual_observable_parts, predicted_observable_parts):
            if not np.array_equal(actual, predicted):
                num_errors += 1
        return(num_errors/n_runs)


if __name__ == "__main__":
    noise_model = CodeCapactiyBitFlipNoise(0.2)
    exp = IdlingExperiment('RotatedSurfaceCode', 3, noise_model)
    num_errors = exp.calculate_ler(1000)
    print(num_errors)

from pickletools import pyunicode
from random import sample
from typing import final
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.compiling.Circuit import Circuit
from main.compiling.Compiler import Compiler
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.compiling.NoiseModel import PhenomenologicalNoise, CodeCapactiyBitFlipNoise
from main.decoding.PymatchingDecoder import PymatchingDecoder
import numpy as np

test_qpu = SquareLatticeQPU((30, 30))
noise_model = CodeCapactiyBitFlipNoise(0.01)
surface_code = RotatedSurfaceCode(3)
test_qpu.embed(surface_code, (0, 0), (0, 1))
test_compiler = Compiler(noise_model)

test_compiler.compile_code(
    surface_code, repeat_block=False, final_block=False)
circuit = Circuit()
circuit.to_stim(test_compiler.gates_at_timesteps,
                test_compiler.detector_qubits)
stim_circuit = circuit.full_circuit

decoder_code_capacity = PymatchingDecoder(
    stim_circuit.detector_error_model(decompose_errors=True))

test_qpu = SquareLatticeQPU((30, 30))
noise_model = PhenomenologicalNoise(0.01, 0.01)
surface_code = RotatedSurfaceCode(3)
test_qpu.embed(surface_code, (0, 0), (0, 1))
test_compiler = Compiler(noise_model)

test_compiler.compile_code(
    surface_code, repeat_block=True, final_block=True)
circuit = Circuit()
circuit.to_stim(test_compiler.gates_at_timesteps,
                test_compiler.detector_qubits,
                n_code_rounds=3)
stim_circuit = circuit.full_circuit

decoder_phenomenological = PymatchingDecoder(
    stim_circuit.detector_error_model(decompose_errors=True))


def test_generate_nx_graph():
    nx_matching_graph = decoder_code_capacity.detector_error_model_to_nx_graph()

    # 4 detectors + 1 boundary node
    assert nx_matching_graph.number_of_nodes() == 5

    # 3 edges between detectors, 4 edges to boundary
    assert nx_matching_graph.number_of_edges() == 7

    nx_matching_graph = decoder_phenomenological.detector_error_model_to_nx_graph()
    assert nx_matching_graph.number_of_nodes() == 13

    # per layer 7 horizontal edges, in total 10 vertical edges
    assert nx_matching_graph.number_of_edges() == 3*7 + 8


def test_nx_graph_to_pymatching_graph():
    nx_matching_graph = decoder_code_capacity.detector_error_model_to_nx_graph()
    pymatching_graph = decoder_code_capacity.nx_graph_to_pymatching_graph(
        nx_matching_graph)
    assert pymatching_graph.num_nodes == 6  # one node is added

    # the added node is connected to all other nodes
    assert pymatching_graph.num_edges == 7+5


def test_decode_samples_code_capacity():
    test_qpu = SquareLatticeQPU((30, 30))
    noise_model = CodeCapactiyBitFlipNoise(0.05)
    surface_code = RotatedSurfaceCode(3)
    test_qpu.embed(surface_code, (0, 0), (0, 1))
    test_compiler = Compiler(noise_model)
    test_compiler.compile_code(
        surface_code, repeat_block=False, final_block=False, measure_data_qubits=True)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps,
                    test_compiler.detector_qubits)
    stim_circuit = circuit.full_circuit
    decoder = PymatchingDecoder(
        stim_circuit.detector_error_model(decompose_errors=True))

    sample_all_zeros = np.zeros(stim_circuit.num_detectors)
    sample_one_error = np.copy(sample_all_zeros)
    sample_one_error[0] = 1

    sample_weight_two_error = np.copy(sample_all_zeros)
    sample_weight_two_error[0] = 1
    sample_weight_two_error[-4] = 1

    predicted_observable_parts = decoder.decode_samples(
        np.array([sample_all_zeros, sample_one_error, sample_weight_two_error]))
    actual_observable_parts = [[False], [True], [False]]
    for actual, predicted in zip(actual_observable_parts, predicted_observable_parts):
        assert actual == predicted


# def test_decode_samples_circuit_level_noise():

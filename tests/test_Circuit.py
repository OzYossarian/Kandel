import random
import stim
from main.compiling.Compiler import Compiler
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.codes.RepetitionCode import RepetitionCode
from main.compiling.Circuit import Circuit
from main.compiling.NoiseModel import (CircuitLevelNoise,
                                       CodeCapactiyBitFlipNoise,
                                       PhenomenologicalNoise)


def test_distance_2_rep_code_1_round_X_code_capacity_noise():
    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)
    test_qpu.embed(rep_code, (0, 0), 0)
    noise_model = CodeCapactiyBitFlipNoise(0.1)
    test_compiler = Compiler(noise_model)
    test_compiler.compile_code(rep_code, repeat_block=False, final_block=False)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps,
                    test_compiler.detector_qubits)
    assert circuit.full_circuit == stim.Circuit("""R 0 1 2
                                                X_ERROR(0.1) 0 1
                                                TICK
                                                CX 0 2
                                                TICK
                                                CX 1 2
                                                TICK
                                                MR 2
                                                DETECTOR rec[-1]
                                                TICK""")


def test_distance_2_rep_code_2_rounds_phenomenological_noise():
    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)
    test_qpu.embed(rep_code, (0, 0), 0)
    noise_model = PhenomenologicalNoise(0.1, 0.1)
    test_compiler = Compiler(noise_model)
    test_compiler.compile_code(
        rep_code, measure_data_qubits=True)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps,
                    test_compiler.detector_qubits, n_code_rounds=3)
    assert circuit.full_circuit == stim.Circuit("""R 0 1 2
                                                DEPOLARIZE1(0.1) 0 1
                                                TICK
                                                CX 0 2
                                                TICK
                                                CX 1 2
                                                X_ERROR(0.1) 2
                                                TICK
                                                MR 2
                                                DETECTOR rec[-1]
                                                TICK
                                                REPEAT 1 {
                                                    R 2
                                                    DEPOLARIZE1(0.1) 0 1
                                                    TICK
                                                    CX 0 2
                                                    TICK
                                                    CX 1 2
                                                    X_ERROR(0.1) 2
                                                    TICK
                                                    MR 2
                                                    DETECTOR rec[-1] rec[-2]
                                                    TICK
                                                }
                                                R 2
                                                DEPOLARIZE1(0.1) 0 1
                                                TICK
                                                CX 0 2
                                                TICK
                                                CX 1 2
                                                X_ERROR(0.1) 2
                                                TICK
                                                MR 2
                                                DETECTOR rec[-1] rec[-2]
                                                MR 0 1
                                                DETECTOR rec[-1] rec[-2] rec[-3]
                                                OBSERVABLE_INCLUDE(0) rec[-2]
                                                TICK""")


def test_distance_2_rep_code_10_rounds():
    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)
    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()
    test_compiler.compile_code(
        rep_code)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps,
                    test_compiler.detector_qubits, n_code_rounds=10)
    assert circuit.full_circuit == stim.Circuit("""R 0 1 2
                                                TICK
                                                CX 0 2
                                                TICK
                                                CX 1 2
                                                TICK
                                                MR 2
                                                DETECTOR rec[-1]
                                                TICK
                                                REPEAT 8 {
                                                    R 2
                                                    TICK
                                                    CX 0 2
                                                    TICK
                                                    CX 1 2
                                                    TICK
                                                    MR 2
                                                    DETECTOR rec[-1] rec[-2]
                                                    TICK
                                                }
                                                R 2
                                                TICK
                                                CX 0 2
                                                TICK
                                                CX 1 2
                                                TICK
                                                MR 2
                                                DETECTOR rec[-1] rec[-2]
                                                TICK""")


def test_distance_4_rep_code_5_rounds_circuit_level_noise():
    test_qpu = SquareLatticeQPU((8, 1))
    rep_code = RepetitionCode(4)
    test_qpu.embed(rep_code, (0, 0), 0)

    noise_model = CircuitLevelNoise(0.1, 0.11, 0.15, 0.2)
    test_compiler = Compiler(noise_model)
    test_compiler.compile_code(
        rep_code, measure_data_qubits=True)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps,
                    test_compiler.detector_qubits, n_code_rounds=5)
    circuit.full_circuit == stim.Circuit("""R 0 1 2 3 4 5 6
                                        X_ERROR(0.11) 0 1 2 3 4 5 6
                                        TICK
                                        CX 0 4 1 5 2 6
                                        DEPOLARIZE2(0.15) 0 4 1 5 2 6
                                        DEPOLARIZE1(0.1) 3
                                        TICK
                                        CX 1 4 2 5 3 6
                                        DEPOLARIZE2(0.15) 1 4
                                        X_ERROR(0.2) 4
                                        DEPOLARIZE2(0.15) 2 5
                                        X_ERROR(0.2) 5
                                        DEPOLARIZE2(0.15) 3 6
                                        X_ERROR(0.2) 6
                                        DEPOLARIZE1(0.1) 0
                                        TICK
                                        MR 4
                                        DETECTOR rec[-1]
                                        MR 5
                                        DETECTOR rec[-1]
                                        MR 6
                                        DETECTOR rec[-1]
                                        DEPOLARIZE1(0.1) 0 3 1 2
                                        TICK
                                        REPEAT 3 {
                                            R 4 5 6
                                            X_ERROR(0.11) 4 5 6
                                            DEPOLARIZE1(0.1) 0 1 2 3
                                            TICK
                                            CX 0 4 1 5 2 6
                                            DEPOLARIZE2(0.15) 0 4 1 5 2 6
                                            DEPOLARIZE1(0.1) 3
                                            TICK
                                            CX 1 4 2 5 3 6
                                            DEPOLARIZE2(0.15) 1 4
                                            X_ERROR(0.2) 4
                                            DEPOLARIZE2(0.15) 2 5
                                            X_ERROR(0.2) 5
                                            DEPOLARIZE2(0.15) 3 6
                                            X_ERROR(0.2) 6
                                            DEPOLARIZE1(0.1) 0
                                            TICK
                                            MR 4
                                            DETECTOR rec[-1] rec[-4]
                                            MR 5
                                            DETECTOR rec[-1] rec[-4]
                                            MR 6
                                            DETECTOR rec[-1] rec[-4]
                                            DEPOLARIZE1(0.1) 0 3 1 2
                                            TICK
                                        }
                                        R 4 5 6
                                        X_ERROR(0.11) 4 5 6
                                        DEPOLARIZE1(0.1) 0 1 2 3
                                        TICK
                                        CX 0 4 1 5 2 6
                                        DEPOLARIZE2(0.15) 0 4 1 5 2 6
                                        DEPOLARIZE1(0.1) 3
                                        TICK
                                        CX 1 4 2 5 3 6
                                        DEPOLARIZE2(0.15) 1 4
                                        X_ERROR(0.2) 4
                                        DEPOLARIZE2(0.15) 2 5
                                        X_ERROR(0.2) 5
                                        DEPOLARIZE2(0.15) 3 6
                                        X_ERROR(0.2) 6 0
                                        DEPOLARIZE1(0.1) 0
                                        X_ERROR(0.2) 1 2 3
                                        TICK
                                        MR 4
                                        DETECTOR rec[-1] rec[-4]
                                        MR 5
                                        DETECTOR rec[-1] rec[-4]
                                        MR 6
                                        DETECTOR rec[-1] rec[-4]
                                        MR 0 1
                                        DETECTOR rec[-1] rec[-2] rec[-5]
                                        MR 2
                                        DETECTOR rec[-1] rec[-2] rec[-5]
                                        MR 3
                                        DETECTOR rec[-1] rec[-2] rec[-5]
                                        OBSERVABLE_INCLUDE(0) rec[-4]
                                        TICK""")


def test_distance_2_rep_code_2_rounds_measure_data_qubits():
    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)
    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()

    test_compiler.compile_code(
        rep_code, repeat_block=False, measure_data_qubits=True)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps,
                    test_compiler.detector_qubits)
    assert circuit.full_circuit == stim.Circuit("""R 0 1 2
                                                     TICK
                                                     CX 0 2
                                                     TICK
                                                     CX 1 2
                                                     TICK
                                                     MR 2
                                                     DETECTOR rec[-1]
                                                     TICK
                                                     R 2
                                                     TICK
                                                     CX 0 2
                                                     TICK
                                                     CX 1 2
                                                     TICK
                                                     MR 2
                                                     DETECTOR rec[-1] rec[-2]
                                                     MR 0 1
                                                     DETECTOR rec[-1] rec[-2] rec[-3]
                                                     OBSERVABLE_INCLUDE(0) rec[-2]
                                                     TICK""")


def test_distance_4_rep_code_2_rounds_measure_data_qubits():
    test_qpu = SquareLatticeQPU((7, 1))
    rep_code = RepetitionCode(4)
    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()
    test_compiler.compile_code(
        rep_code, final_block=False, measure_data_qubits=True)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps,
                    test_compiler.detector_qubits)
    assert circuit.full_circuit == stim.Circuit("""R 0 1 2 3 4 5 6
                                                TICK
                                                CX 0 4 1 5 2 6
                                                TICK
                                                CX 1 4 2 5 3 6
                                                TICK
                                                MR 4
                                                DETECTOR rec[-1]
                                                MR 5
                                                DETECTOR rec[-1]
                                                MR 6
                                                DETECTOR rec[-1]
                                                TICK
                                                R 4 5 6
                                                TICK
                                                CX 0 4 1 5 2 6
                                                TICK
                                                CX 1 4 2 5 3 6
                                                TICK
                                                MR 4
                                                DETECTOR rec[-1] rec[-4]
                                                MR 5
                                                DETECTOR rec[-1] rec[-4]
                                                MR 6
                                                DETECTOR rec[-1] rec[-4]
                                                MR 0 1
                                                DETECTOR rec[-1] rec[-2] rec[-5]
                                                MR 2
                                                DETECTOR rec[-1] rec[-2] rec[-5]
                                                MR 3
                                                DETECTOR rec[-1] rec[-2] rec[-5]
                                                OBSERVABLE_INCLUDE(0) rec[-4]
                                                TICK
                                                """)


def test_distance_3_surface_code_code_capacity():
    test_qpu = SquareLatticeQPU((10, 10))
    noise_model = CodeCapactiyBitFlipNoise(0.1)
    surface_code = RotatedSurfaceCode(3)
    test_qpu.embed(surface_code, (0, 0), (0, 1))
    test_compiler = Compiler(noise_model)

    test_compiler.compile_code(
        surface_code, repeat_block=False, final_block=False, measure_data_qubits=True)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps,
                    test_compiler.detector_qubits)
    assert str(circuit.full_circuit[1]) == "X_ERROR(0.1) 0 1 2 3 4 5 6 7 8"
    assert circuit.full_circuit.num_detectors == 8
    assert circuit.full_circuit.num_observables == 1
    assert circuit.full_circuit.num_qubits == 17


def test_distance_5_surface_code_1_round_phenomenological_noise():
    test_qpu = SquareLatticeQPU((10, 10))
    noise_model = PhenomenologicalNoise(0.1, 0.2)
    surface_code = RotatedSurfaceCode(3)
    test_qpu.embed(surface_code, (0, 0), (0, 1))
    test_compiler = Compiler(noise_model)

    test_compiler.compile_code(
        surface_code, repeat_block=False, final_block=False)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps,
                    test_compiler.detector_qubits)

    assert circuit.full_circuit == stim.Circuit("""R 0 1 2 3 4 5 6 7 8 9 10 11
                                                    DEPOLARIZE1(0.1) 0 1 2 3 4 5 6 7 8
                                                    TICK
                                                    R 12
                                                    H 9 10
                                                    R 13 14
                                                    H 11
                                                    TICK
                                                    CX 4 12 9 5 10 7 8 13 2 14 11 3
                                                    R 15
                                                    TICK
                                                    CX 3 12 9 2 10 6 5 13 1 14
                                                    R 16
                                                    CX 11 0
                                                    H 15
                                                    X_ERROR(0.2) 14
                                                    TICK
                                                    CX 1 12 9 4 10 4 7 13
                                                    MR 14
                                                    DETECTOR rec[-1]
                                                    CX 7 16
                                                    H 11
                                                    CX 15 8
                                                    X_ERROR(0.2) 11
                                                    TICK
                                                    CX 0 12 9 1 10 3 4 13 6 16
                                                    MR 11
                                                    CX 15 5
                                                    X_ERROR(0.2) 12 13 16
                                                    TICK
                                                    MR 12
                                                    DETECTOR rec[-1]
                                                    H 9 10
                                                    MR 13
                                                    DETECTOR rec[-1]
                                                    MR 16
                                                    DETECTOR rec[-1]
                                                    H 15
                                                    X_ERROR(0.2) 9 10 15
                                                    TICK
                                                    MR 9 10 15
                                                    TICK
                                    """)


def test_distance_3_surface_code_1_round_circuit_level_noise():
    test_qpu = SquareLatticeQPU((10, 10))
    noise_model = CircuitLevelNoise(0.1, 0.2, 0.3, 0.4)
    surface_code = RotatedSurfaceCode(3)
    test_qpu.embed(surface_code, (0, 0), (0, 1))
    test_compiler = Compiler(noise_model)

    test_compiler.compile_code(
        surface_code, repeat_block=False,
        final_block=False, measure_data_qubits=True)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps,
                    test_compiler.detector_qubits)
    assert circuit.full_circuit.num_observables == 1
    assert circuit.full_circuit.num_detectors == 8


def test_distance_5_surface_code_5_rounds_phenomenological_noise():
    test_qpu = SquareLatticeQPU((10, 10))
    noise_model = PhenomenologicalNoise(0.1, 0.2)
    surface_code = RotatedSurfaceCode(5)
    test_qpu.embed(surface_code, (0, 0), (0, 1))
    test_compiler = Compiler(noise_model)

    test_compiler.compile_code(surface_code,
                               measure_data_qubits=True)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps,
                    test_compiler.detector_qubits,
                    5)
    assert circuit.full_circuit.num_detectors == 6*12
    assert circuit.full_circuit.num_observables == 1
    assert circuit.full_circuit.num_qubits == 49

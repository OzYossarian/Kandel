from main.Circuit import Circuit
from main.NoiseModel import CodeCapactiyBitFlipNoise, PhenomenologicalNoise
from main.building_blocks.Qubit import Qubit
from main.codes.RepetitionCode import RepetitionCode
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.enums import State
from main. Compiler import Compiler
from main.building_blocks.Pauli import Pauli, PauliX, PauliY, PauliZ
import stim


def test_distance_2_rep_code_1_round_X_code_capacity_noise():
    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)
    test_qpu.embed(rep_code, (0, 0), 0)
    noise_model = CodeCapactiyBitFlipNoise(0.1)
    test_compiler = Compiler(noise_model)
    test_compiler.compile_code(rep_code, n_code_rounds=1)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps)
    assert circuit.stim_circuit == stim.Circuit("""R 0 1 2      
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
        rep_code, n_code_rounds=2)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps)
    assert circuit.stim_circuit == stim.Circuit("""R 0 1 2
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
                                                    TICK""")


def test_distance_2_rep_code_2_rounds():
    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)
    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()

    test_compiler.compile_code(
        rep_code, n_code_rounds=2)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps)
    assert circuit.stim_circuit == stim.Circuit("""R 0 1 2
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
                                                     TICK""")


def test_distance_2_rep_code_2_rounds_measure_data_qubits():
    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)
    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()

    test_compiler.compile_code(
        rep_code, n_code_rounds=2, measure_data_qubits=True)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps)
    print(circuit.stim_circuit, 'stim')
    assert circuit.stim_circuit == stim.Circuit("""R 0 1 2
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
        rep_code, n_code_rounds=2, measure_data_qubits=True)
    circuit = Circuit()
    circuit.to_stim(test_compiler.gates_at_timesteps)
    assert circuit.stim_circuit == stim.Circuit("""R 0 1 2 3 4 5 6
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

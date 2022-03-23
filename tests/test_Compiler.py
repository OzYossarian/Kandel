from main.Compiler import Compiler
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.codes.RepetitionCode import RepetitionCode
from main.printing.Printer2D import Printer2D
from main.Circuit import Circuit
import stim


def test_compile_qpu():
    pass
    assert test_circuit == stim.Circuit("""R 0 1 2 3 4 5 6  
                                                 CNOT 0 1 2 3 4 5
                                                 CNOT 2 1 4 3 6 5
                                                 MR 1 3 5""")


def test_compile_code():
    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)
    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()

    test_compiler.compile_code(
        rep_code, n_code_rounds=1)
    gate_dict = {}
    for qubit in rep_code.data_qubits.values():
        gate_dict[qubit] = 'RZ'
    for qubit in rep_code.ancilla_qubits.values():
        gate_dict[qubit] = 'RZ'
    assert test_compiler.gates_at_timesteps[0]['gates'] == gate_dict

    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)
    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()

    test_compiler.compile_code(
        rep_code, n_code_rounds=2)
    gate_dict = {}
    for qubit in rep_code.data_qubits.values():
        gate_dict[qubit] = 'RZ'
    for qubit in rep_code.ancilla_qubits.values():
        gate_dict[qubit] = 'RZ'
    assert test_compiler.gates_at_timesteps[0]['gates'] == gate_dict
    gate_dict_2 = {}
    for qubit in rep_code.ancilla_qubits.values():
        gate_dict_2[qubit] = 'RZ'
    assert test_compiler.gates_at_timesteps[4]['gates'] == gate_dict_2
    print(test_compiler.gates_at_timesteps[6]['gates'])

    # TODO update timestep


test_compile_code()


def test_initialize_qubits():
    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)

    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()
    test_compiler.initialize_qubits(rep_code.data_qubits.values(), 0)
    assert test_compiler.gates_at_timesteps[0]['gates'] == {
        rep_code.data_qubits[0]: 'RZ', rep_code.data_qubits[2]: 'RZ'}


def test_compile_one_round():
    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)

    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()
    test_compiler.compile_one_round(
        test_qpu.codes[1].schedule[0], 0)
    gate_dict = {}
    for qubit in rep_code.data_qubits.values():
        gate_dict[qubit] = 'RZ'
    for qubit in rep_code.ancilla_qubits.values():
        gate_dict[qubit] = 'RZ'
    test_compiler.initialize_qubits(rep_code.data_qubits.values(), 0)
    assert test_compiler.gates_at_timesteps[0]['gates'] == gate_dict

    test_qpu = SquareLatticeQPU((7, 1))
    rep_code = RepetitionCode(4)

    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()
    test_circuit = Circuit()
    test_compiler.compile_one_round(
        test_qpu.codes[1].schedule[0], 0)
    test_compiler.initialize_qubits(rep_code.data_qubits.values(), 0)
    gate_dict = {}
    for qubit in rep_code.data_qubits.values():
        gate_dict[qubit] = 'RZ'
    for qubit in rep_code.ancilla_qubits.values():
        gate_dict[qubit] = 'RZ'
    assert test_compiler.gates_at_timesteps[0]['gates'] == gate_dict

    gate_dict_t1 = {}
    gate_dict_t2 = {}
    gate_dict_t3 = {}
    for check in rep_code.checks:

        gate_dict_t1[check.operators[0].qubit, check.ancilla] = "CNOT"
        gate_dict_t2[check.operators[1].qubit, check.ancilla] = "CNOT"

        gate_dict_t3[check.ancilla] = "MRZ"
    assert test_compiler.gates_at_timesteps[1]['gates'] == gate_dict_t1
    assert test_compiler.gates_at_timesteps[2]['gates'] == gate_dict_t2
    assert test_compiler.gates_at_timesteps[3]['gates'] == gate_dict_t3

    assert test_compiler.gates_at_timesteps[3]['initialized_qubits'] == set(
        rep_code.data_qubits.values())

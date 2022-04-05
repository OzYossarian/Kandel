from main.Compiler import Compiler
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.codes.RepetitionCode import RepetitionCode
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.printing.Printer2D import Printer2D
from main.Circuit import Circuit
import stim


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
        rep_code, n_code_rounds=1, measure_data_qubits=True)

    gate_dict = {}
    gate_measure_dict = {}
    data_qubits = tuple()
    for qubit in rep_code.data_qubits.values():
        gate_dict[qubit] = 'RZ'
        data_qubits += (qubit,)

    for qubit in rep_code.ancilla_qubits.values():
        gate_dict[qubit] = 'RZ'

        gate_measure_dict[(data_qubits, (qubit,))] = 'MRZ'
        gate_measure_dict[qubit] = 'MRZ'

    gate_measure_dict[(rep_code.data_qubits[0],)] = 'Observable'
    assert test_compiler.gates_at_timesteps[0]['gates'] == gate_dict
    assert test_compiler.gates_at_timesteps[3]['gates'] == gate_measure_dict

    test_qpu = SquareLatticeQPU((7, 1))
    rep_code = RepetitionCode(4)
    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()

    test_compiler.compile_code(
        rep_code, n_code_rounds=1)
    gate_dict = {}
    measurement_dict = {}
    for qubit in rep_code.data_qubits.values():
        gate_dict[qubit] = 'RZ'
    for qubit in rep_code.ancilla_qubits.values():
        gate_dict[qubit] = 'RZ'
        measurement_dict[qubit] = 'MRZ'

    assert test_compiler.gates_at_timesteps[0]['gates'] == gate_dict
    assert test_compiler.gates_at_timesteps[3]['gates'] == measurement_dict

    test_compiler_2_rounds = Compiler()

    test_compiler_2_rounds.compile_code(
        rep_code, n_code_rounds=2)
    gate_dict = {}

    for i in range(3):
        assert test_compiler_2_rounds.gates_at_timesteps[i][
            'gates'] == test_compiler.gates_at_timesteps[i]['gates']

    for i in range(5, 8):
        assert test_compiler_2_rounds.gates_at_timesteps[i][
            'gates'] == test_compiler.gates_at_timesteps[i-4]['gates']

    test_compiler_3_rounds = Compiler()

    test_compiler_3_rounds.compile_code(
        rep_code, n_code_rounds=3)

    for i in range(3):
        assert test_compiler_3_rounds.gates_at_timesteps[i][
            'gates'] == test_compiler.gates_at_timesteps[i]['gates']

    for i in range(5, 8):
        assert test_compiler_3_rounds.gates_at_timesteps[i][
            'gates'] == test_compiler.gates_at_timesteps[i-4]['gates']

    for i in range(9, 12):
        assert test_compiler_3_rounds.gates_at_timesteps[i][
            'gates'] == test_compiler.gates_at_timesteps[i-8]['gates']


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


def test_compile_rotated_surface_code():
    test_qpu = SquareLatticeQPU((10, 10))
    sc = RotatedSurfaceCode(3)
    test_qpu.embed(sc, (0, 0), (0, 1))
    test_compiler = Compiler()
    test_compiler.compile_one_round(
        test_qpu.codes[1].schedule[0], 0)

    gate_dict = {}
    for qubit in sc.data_qubits.values():
        gate_dict[qubit] = 'RZ'
    for qubit in sc.ancilla_qubits.values():
        gate_dict[qubit] = 'RZ'

    print(gate_dict, 'gate dict')
    print(test_compiler.gates_at_timesteps[0]['gates'], '\n')
    print(test_compiler.gates_at_timesteps[1]['gates'], '\n')
    print(test_compiler.gates_at_timesteps[2]['gates'], '\n')
    print(test_compiler.gates_at_timesteps[3]['gates'])


test_compile_rotated_surface_code()

from main.compiling.Compiler import Compiler
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.codes.RepetitionCode import RepetitionCode
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.compiling.Circuit import Circuit


def test_compile_code():
    test_qpu = SquareLatticeQPU((3, 1))
    rep_code = RepetitionCode(2)
    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()

    test_compiler.compile_code(
        rep_code, repeat_block=False, final_block=False)
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
        rep_code, repeat_block=False, final_block=False, measure_data_qubits=True)

    gate_dict = {}
    gate_measure_dict = {}
    data_qubits = tuple()
    for qubit in rep_code.data_qubits.values():
        gate_dict[qubit] = 'RZ'
        data_qubits += (qubit,)

    for qubit in rep_code.ancilla_qubits.values():
        gate_dict[qubit] = 'RZ'

        gate_measure_dict[((data_qubits), (), qubit)] = 'MRZ'
        gate_measure_dict[qubit] = 'MRZ'

    gate_measure_dict[(rep_code.data_qubits[0],)] = 'Observable'

    assert test_compiler.gates_at_timesteps[0]['gates'] == gate_dict
    assert test_compiler.gates_at_timesteps[3]['gates'] == gate_measure_dict

    test_qpu = SquareLatticeQPU((7, 1))
    rep_code = RepetitionCode(4)
    test_qpu.embed(rep_code, (0, 0), 0)
    test_compiler = Compiler()

    test_compiler.compile_code(
        rep_code, repeat_block=False, final_block=False)
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
        rep_code, repeat_block=False, final_block=True)
    gate_dict = {}

    for i in range(3):
        assert test_compiler_2_rounds.gates_at_timesteps[i][
            'gates'] == test_compiler.gates_at_timesteps[i]['gates']

    for i in range(5, 8):
        assert test_compiler_2_rounds.gates_at_timesteps[i][
            'gates'] == test_compiler.gates_at_timesteps[i-4]['gates']

    test_compiler_3_rounds = Compiler()

    test_compiler_3_rounds.compile_code(
        rep_code, repeat_block=True, final_block=True)

    for i in range(3):
        assert test_compiler_3_rounds.gates_at_timesteps[i][
            'gates'] == test_compiler.gates_at_timesteps[i]['gates']

    for i in range(5, 8):
        assert test_compiler_3_rounds.gates_at_timesteps[i][
            'gates'] == test_compiler.gates_at_timesteps[i-4]['gates']


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
    test_compiler.initialize_qubits(rep_code.data_qubits.values(), 0)
    test_compiler.compile_one_round(
        test_qpu.codes[1].schedule[0], 0)

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


def test_compile_rotated_surface_code_three_rounds():
    test_qpu = SquareLatticeQPU((10, 10))
    sc = RotatedSurfaceCode(3)
    test_qpu.embed(sc, (0, 0), (0, 1))
    test_compiler = Compiler()
    test_compiler.initialize_qubits(sc.data_qubits.values(), 0)
    test_compiler.compile_code(
        test_qpu.codes[1], measure_data_qubits=True)

    gate_dict_0 = {}
    gate_dict_1 = {}
    for data_q in sc.data_qubits.values():
        gate_dict_0[data_q] = 'RZ'
    for check in sc.schedule[0]:
        if check.initialization_timestep == 0:
            gate_dict_0[check.ancilla] = 'RZ'
            gate_dict_1[check.ancilla] = 'H'
        elif check.initialization_timestep == 1:
            gate_dict_1[check.ancilla] = 'RZ'

    gate_dict_2 = {sc.ancilla_qubits[(4, 1)]: 'RZ',
                   ((sc.data_qubits[(4, 2)]), (sc.ancilla_qubits[(3, 2)])): 'CNOT',
                   ((sc.data_qubits[(2, 2)]), (sc.ancilla_qubits[(1, 2)])): 'CNOT',
                   ((sc.data_qubits[(2, 0)]), (sc.ancilla_qubits[(1, 0)])): 'CNOT',
                   ((sc.ancilla_qubits[(2, 1)]), (sc.data_qubits[(3, 1)])): 'CNOT',
                   ((sc.ancilla_qubits[(2, 3)]), (sc.data_qubits[(3, 3)])): 'CNOT',
                   ((sc.ancilla_qubits[(0, 3)]), (sc.data_qubits[(1, 3)])): 'CNOT'}

    assert test_compiler.gates_at_timesteps[0]['gates'] == gate_dict_0
    assert test_compiler.gates_at_timesteps[1]['gates'] == gate_dict_1
    assert len(test_compiler.gates_at_timesteps[2]['initialized_qubits']) == 16
    assert test_compiler.gates_at_timesteps[2]['gates'] == gate_dict_2


def test_compile_rotated_surface_code_one_round():
    test_qpu = SquareLatticeQPU((10, 10))
    sc = RotatedSurfaceCode(3)
    test_qpu.embed(sc, (0, 0), (0, 1))
    test_compiler = Compiler()
    test_compiler.initialize_qubits(sc.data_qubits.values(), 0)
    test_compiler.compile_one_round(
        test_qpu.codes[1].schedule[0], 0)

    gate_dict_0 = {}
    gate_dict_1 = {}
    for data_q in sc.data_qubits.values():
        gate_dict_0[data_q] = 'RZ'
    for check in sc.schedule[0]:
        if check.initialization_timestep == 0:
            gate_dict_0[check.ancilla] = 'RZ'
            gate_dict_1[check.ancilla] = 'H'
        elif check.initialization_timestep == 1:
            gate_dict_1[check.ancilla] = 'RZ'

    gate_dict_2 = {sc.ancilla_qubits[(4, 1)]: 'RZ',
                   ((sc.data_qubits[(4, 2)]), (sc.ancilla_qubits[(3, 2)])): 'CNOT',
                   ((sc.data_qubits[(2, 2)]), (sc.ancilla_qubits[(1, 2)])): 'CNOT',
                   ((sc.data_qubits[(2, 0)]), (sc.ancilla_qubits[(1, 0)])): 'CNOT',
                   ((sc.ancilla_qubits[(2, 1)]), (sc.data_qubits[(3, 1)])): 'CNOT',
                   ((sc.ancilla_qubits[(2, 3)]), (sc.data_qubits[(3, 3)])): 'CNOT',
                   ((sc.ancilla_qubits[(0, 3)]), (sc.data_qubits[(1, 3)])): 'CNOT'}

    assert test_compiler.gates_at_timesteps[0]['gates'] == gate_dict_0
    assert test_compiler.gates_at_timesteps[1]['gates'] == gate_dict_1
    assert len(test_compiler.gates_at_timesteps[2]['initialized_qubits']) == 16
    assert test_compiler.gates_at_timesteps[2]['gates'] == gate_dict_2
    assert len(test_compiler.gates_at_timesteps[7]['gates']) == 3

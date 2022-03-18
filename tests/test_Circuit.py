from sre_parse import State
from main.Circuit import Circuit
from main.building_blocks.Qubit import Qubit
from main.codes.RepetitionCode import RepetitionCode
from main.enums import State
import stim


def test_initialize_qubits():
    q_2_0 = Qubit((2, 0), State(0))
    test_circuit = Circuit()
    test_circuit.initialize_qubits([q_2_0])
    assert test_circuit.initialized_qubit_coordinates == {(2, 0)}
    assert test_circuit.coord_to_stim_index == {(2, 0): 0}
    assert test_circuit.stim_circuit == stim.Circuit("R 0")

    q_4_0 = Qubit((4, 0), State(0))
    test_circuit.initialize_qubits([q_4_0])
    assert test_circuit.initialized_qubit_coordinates == {(2, 0), (4, 0)}
    assert test_circuit.coord_to_stim_index == {(2, 0): 0, (4, 0): 1}
    assert test_circuit.stim_circuit == stim.Circuit("R 0 1")

    test_circuit.initialize_qubits([q_2_0])
    assert test_circuit.initialized_qubit_coordinates == {(2, 0), (4, 0)}
    assert test_circuit.coord_to_stim_index == {(2, 0): 0, (4, 0): 1}
    assert test_circuit.stim_circuit == stim.Circuit("R 0 1")


def test_compile_check_cnot():
    rep_code = RepetitionCode(3)
    check_a1_d0_d2 = rep_code.schedule[0][0]
    test_circuit = Circuit()
    data_qubits = [check_a1_d0_d2.operators[i].qubit for i in range(
        len(check_a1_d0_d2.operators))]
    data_qubits.append(check_a1_d0_d2.ancilla)
    test_circuit.initialize_qubits(data_qubits)
    test_circuit.check_to_stim_cnot(check_a1_d0_d2)
    assert test_circuit.stim_circuit == stim.Circuit("""R 0 1 2
                                                     CX 0 2 1 2""")
    check_a3_d2_d4 = rep_code.schedule[0][1]
    data_qubits = [check_a3_d2_d4.operators[i].qubit for i in range(
        len(check_a3_d2_d4.operators))]
    data_qubits.append(check_a3_d2_d4.ancilla)
    test_circuit.initialize_qubits(data_qubits)
    test_circuit.check_to_stim_cnot(check_a3_d2_d4)
    print(test_circuit.stim_circuit, 'stim_circuit')
    assert test_circuit.stim_circuit == stim.Circuit("""R 0 1 2 
                                                     CX 0 2 1 2
                                                     R 3 4
                                                     CX 1 4 3 4""")
    # TODO create
    assert test_circuit.stim_circuit == stim.Circuit("""R 0 1 2 3 4
                                                     CX 0 2 1 2 1 4 3 4""")


test_compile_check_cnot()

from collections import defaultdict
import copy
import pytest
import stim

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.compiling.Circuit import Circuit
from main.compiling.Instruction import Instruction
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models import CodeCapacityBitFlipNoise
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise

from main.compiling.syndrome_extraction.controlled_gate_orderers.RotatedSurfaceCodeOrderer import (
    RotatedSurfaceCodeOrderer,
)
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import (
    CxCyCzExtractor,
)
from main.utils.enums import State


single_qubit_circuit = Circuit()
qubit = Qubit(1)
single_qubit_circuit.initialise(0, Instruction([qubit], "R", is_initialization=True))
single_qubit_circuit.add_instruction(2, Instruction([qubit], "Z"))

two_qubit_circuit = Circuit()
qubit_1 = Qubit(1)
qubit_2 = Qubit(2)
two_qubit_circuit.initialise(0, Instruction([qubit_1], "R", is_initialization=True))
two_qubit_circuit.add_instruction(2, Instruction([qubit_1], "Z"))
two_qubit_circuit.initialise(0, Instruction([qubit_2], "R", is_initialization=True))


circuit_with_resonator_idling = Circuit()
qubit_1 = Qubit(1)
qubit_2 = Qubit(2)
pauli_q1 = Pauli(qubit_1, PauliLetter("Z", 1))
pauli_q2 = Pauli(qubit_2, PauliLetter("Z", 1))
check_q1_Z = Check([pauli_q1], anchor=None)
check_q2_Z = Check([pauli_q2], anchor=None)

circuit_with_resonator_idling.initialise(
    0, Instruction([qubit_1], "R", is_initialization=True)
)
circuit_with_resonator_idling.add_instruction(8, Instruction([qubit_1], "Z"))
circuit_with_resonator_idling.measure(
    Instruction([qubit_1], "M", is_measurement=True), check_q1_Z, 0, 10
)
circuit_with_resonator_idling.initialise(
    2, Instruction([qubit_2], "R", is_initialization=True)
)

circuit_with_resonator_idling.add_instruction(4, Instruction([qubit_1], "Z"))


circuit_with_resonator_idling.measure(
    Instruction([qubit_2], "M", is_measurement=True), check_q2_Z, 0, 6
)

def test_to_circ_string():
    assert single_qubit_circuit.to_cirq_string() == "1: ───R───Z───"


def test_get_number_of_occurences_gates():
    n_R_gates = single_qubit_circuit.number_of_instructions("R")
    assert n_R_gates == 1

    n_X_gates = single_qubit_circuit.number_of_instructions("X")
    assert n_X_gates == 0


def test_qubit_index():
    assert single_qubit_circuit.qubit_index(qubit) == 0
    assert two_qubit_circuit.qubit_index(qubit_1) == 0
    assert two_qubit_circuit.qubit_index(qubit_2) == 1


def test_is_initialised():
    assert single_qubit_circuit.is_initialised(1, qubit)
    assert not single_qubit_circuit.is_initialised(0, qubit_1)


def test_initialise():
    three_qubit_circuit = Circuit()
    q_1 = Qubit(1)
    q_2 = Qubit(2)
    q_3 = Qubit(3)
    with pytest.raises(Exception, match="The instruction has to act on 1 qubit"):
        three_qubit_circuit.initialise(
            0, Instruction([q_1, q_2], "R", is_initialization=True)
        )
    with pytest.raises(
        Exception,
        match="The instruction has to be an instance of the Instruction class with is_initialization set to True.",
    ):
        three_qubit_circuit.initialise(0, Instruction([q_1], "X"))

    three_qubit_circuit.initialise(0, Instruction([q_1], "R", is_initialization=True))
    three_qubit_circuit.initialise(12, Instruction([q_3], "R", is_initialization=True))
    three_qubit_circuit.initialise(4, Instruction([q_3], "R", is_initialization=True))

    init_ticks_test = defaultdict(list)
    init_ticks_test[q_1] = [0]
    init_ticks_test[q_3] = [12, 4]
    assert init_ticks_test == three_qubit_circuit.init_ticks


def test_measure():
    single_measurement_circuit = copy.deepcopy(two_qubit_circuit)

    qubit_to_measure = list(single_measurement_circuit.qubits)[0]
    m_instruction = Instruction([qubit_to_measure], "M", is_measurement=True)

    m_instruction.is_measurement = True
    m_instruction.params = ()
    check = Check([Pauli(qubit_to_measure, PauliLetter("Z"))])
    single_measurement_circuit.measure(m_instruction, check, round=0, tick=4)
    correct_dict = defaultdict(list)
    correct_dict[qubit_to_measure] = [m_instruction]
    # test if the circuit is correctly updated
    assert single_measurement_circuit.instructions[4] == correct_dict

    # test if the measurer is correctly updated
    assert single_measurement_circuit.measurer.measurement_checks == {
        m_instruction: (check, 0)
    }

    # test if circuit.measure_ticks is correctly updated
    correct_measurement_tick_dict = defaultdict(list)
    correct_measurement_tick_dict[qubit_to_measure] = [4]
    assert single_measurement_circuit.measure_ticks == correct_measurement_tick_dict

    # test measure multiple
    two_measurements_circuit = copy.deepcopy(two_qubit_circuit)
    qubit_1 = list(two_measurements_circuit.qubits)[0]
    qubit_2 = list(two_measurements_circuit.qubits)[1]

    m_instruction = Instruction([qubit_1, qubit_2], "M", is_measurement=True)

    m_instruction.params = ()
    check = Check([Pauli(qubit_1, PauliLetter("Z")), Pauli(qubit_2, PauliLetter("Z"))])
    two_measurements_circuit.measure(m_instruction, check, round=0, tick=6)
    correct_dict = {}
    correct_dict[qubit_2] = [m_instruction]
    correct_dict[qubit_1] = [m_instruction]
    # test if the circuit is correctly updated
    assert two_measurements_circuit.instructions[6] == correct_dict

    # test if the measurer is correctly updated

    assert two_measurements_circuit.measurer.measurement_checks == {
        m_instruction: (check, 0)
    }

    # test if circuit.measure_ticks is correctly updated
    correct_measurement_tick_dict = defaultdict(list)
    correct_measurement_tick_dict[qubit_1] = [6]
    correct_measurement_tick_dict[qubit_2] = [6]
    assert two_measurements_circuit.measure_ticks == correct_measurement_tick_dict


def test_to_stim(capfd):
    single_qubit_circuit.to_stim(None, track_progress=False)
    out, _ = capfd.readouterr()
    assert out == ""

    single_qubit_circuit.to_stim(None)
    out, _ = capfd.readouterr()
    assert out != ""


def test__to_stim():
    circuit = single_qubit_circuit._to_stim(None, None, True, None)
    assert stim.Circuit(str(circuit)) == stim.Circuit(
        """QUBIT_COORDS(1) 0
            R 0
            TICK
            Z 0"""
    )


def test_add_iddling_noise_to_circuit_tick():
    two_qubit_circuit = Circuit()
    qubit_1 = Qubit(1)
    qubit_2 = Qubit(2)
    two_qubit_circuit.initialise(0, Instruction([qubit_1], "R", is_initialization=True))
    two_qubit_circuit.add_instruction(2, Instruction([qubit_1], "Z"))
    two_qubit_circuit.initialise(0, Instruction([qubit_2], "R", is_initialization=True))

    two_qubit_circuit.add_idling_noise_to_circuit_tick(two_qubit_circuit.instructions[2], OneQubitNoise(0.1, 0.1, 0.1), set([qubit_1, qubit_2]), 2)
    assert two_qubit_circuit.number_of_instructions("PAULI_CHANNEL_1")  == 1


def test_add_iddling_noise_to_circuit():
    # test if no noise is added
    single_qubit_circuit.add_idling_noise_to_circuit(None)
    n_idling_gates = single_qubit_circuit.number_of_instructions("PAULI_CHANNEL_I")
    assert n_idling_gates == 0

    two_qubit_circuit.add_idling_noise_to_circuit(OneQubitNoise(0.1, 0.1, 0.1))
    n_idling_errors = two_qubit_circuit.number_of_instructions("PAULI_CHANNEL_1")
    assert n_idling_errors == 1


def test_add_resonator_and_gate_idling_noise_to_circuit():
    circuit_with_resonator_idling.add_resonator_and_gate_idling_noise_to_circuit(
        OneQubitNoise(0.1, 0.1, 0.1), OneQubitNoise(0.2, 0.2, 0.2)
    )
    assert circuit_with_resonator_idling.to_stim(None) == stim.Circuit(
        """ 
    QUBIT_COORDS(1) 0
    QUBIT_COORDS(2) 1
    R 0
    TICK
    R 1
    TICK
    PAULI_CHANNEL_1(0.2, 0.2, 0.2) 0
    TICK
    Z 0
    TICK
    PAULI_CHANNEL_1(0.1, 0.1, 0.1) 1
    TICK
    M 1
    TICK
    PAULI_CHANNEL_1(0.2, 0.2, 0.2) 0
    TICK
    Z 0
    TICK
    M 0
    """
    )

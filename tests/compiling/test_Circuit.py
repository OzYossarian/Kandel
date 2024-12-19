import random
from collections import defaultdict
import copy
import pytest
import stim
from pytest_mock import MockerFixture
from copy import deepcopy

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.compiling.Circuit import Circuit, RepeatBlock
from main.compiling.Instruction import Instruction
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models import CodeCapacityBitFlipNoise
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise

from main.compiling.syndrome_extraction.controlled_gate_orderers.RotatedSurfaceCodeOrderer import (
    RotatedSurfaceCodeOrderer,
)
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
from main.utils.enums import State

single_qubit_circuit = Circuit()
qubit = Qubit(1)
single_qubit_circuit.initialise(0, Instruction([qubit], "R"))
single_qubit_circuit.add_instruction(2, Instruction([qubit], "Z"))

two_qubit_circuit = Circuit()
qubit_1 = Qubit(1)
qubit_2 = Qubit(2)
two_qubit_circuit.initialise(0, Instruction([qubit_1], "R"))
two_qubit_circuit.add_instruction(2, Instruction([qubit_1], "Z"))
two_qubit_circuit.initialise(0, Instruction([qubit_2], "R"))

circuit_with_two_gates_on_same_qubit = Circuit()
busy_qubit = Qubit(1)
circuit_with_two_gates_on_same_qubit.initialise(
    0, Instruction([busy_qubit], "R"))
idling_noise_1 = OneQubitNoise(0.1, 0.1, 0.1).instruction([busy_qubit])
idling_noise_2 = OneQubitNoise(0.2, 0.2, 0.2).instruction([busy_qubit])
circuit_with_two_gates_on_same_qubit.add_instruction(1, idling_noise_1)
circuit_with_two_gates_on_same_qubit.add_instruction(1, idling_noise_2)

circuit_with_resonator_idle = Circuit()
qubit_1 = Qubit(1)
qubit_2 = Qubit(2)
circuit_with_resonator_idle.initialise(0, Instruction([qubit_1], "R"))
circuit_with_resonator_idle.initialise(0, Instruction([qubit_2], "R"))
circuit_with_resonator_idle.add_instruction(2, Instruction([qubit_1], "Z"))
circuit_with_resonator_idle.add_instruction(
    4, Instruction([qubit_2], "MX", is_measurement=True))
circuit_with_resonator_idle.add_instruction(6, Instruction([qubit_2], "H"))
circuit_with_resonator_idle.add_instruction(
    6, Instruction([qubit_1], "MZ", is_measurement=True))


def create_rsc_circuit():
    code = RotatedSurfaceCode(3)
    syndrome_extractor = CxCyCzExtractor(RotatedSurfaceCodeOrderer())
    noise_model = CodeCapacityBitFlipNoise(0.1)
    rsc_qubits = list(code.data_qubits.values())
    rsc_initials = {qubit: State.Zero for qubit in rsc_qubits}
    compiler = AncillaPerCheckCompiler(noise_model, syndrome_extractor)
    initial_detector_schedules, tick, rsc_circuit = compiler.compile_initialisation(
        code, rsc_initials, None
    )

    rsc_finals = [Pauli(qubit, PauliLetter('Z')) for qubit in rsc_qubits]
    tick = compiler.compile_layer(
        0,
        initial_detector_schedules[0],
        [code.logical_qubits[0].z],
        tick - 2,
        rsc_circuit,
        code,
    )
    compiler.compile_final_measurements(
        rsc_finals,
        None,
        [code.logical_qubits[0].z],
        1,
        tick - 2,
        rsc_circuit,
        code,
    )
    return rsc_circuit


def test_to_circ_string():
    assert single_qubit_circuit.to_cirq_string() == "1: ───R───Z───"


def test_get_number_of_occurrences_gates():
    n_R_gates = single_qubit_circuit.number_of_instructions(["R"])
    assert n_R_gates == 1

    n_X_gates = single_qubit_circuit.number_of_instructions(["X"])
    assert n_X_gates == 0


test_get_number_of_occurrences_gates()


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
    with pytest.raises(Exception, match='The instruction has to act on 1 qubit'):
        three_qubit_circuit.initialise(0, Instruction([q_1, q_2], "R"))
    with pytest.raises(Exception, match='The instruction has to be an initialize instruction starting with \"R\"'):
        three_qubit_circuit.initialise(0, Instruction([q_1], "X"))

    three_qubit_circuit.initialise(0, Instruction([q_1], "R"))
    three_qubit_circuit.initialise(12, Instruction([q_3], "R"))
    three_qubit_circuit.initialise(4, Instruction([q_3], "R"))

    init_ticks_test = defaultdict(list)
    init_ticks_test[q_1] = [0]
    init_ticks_test[q_3] = [12, 4]
    assert init_ticks_test == three_qubit_circuit.init_ticks


def test_measure():
    single_measurement_circuit = copy.deepcopy(two_qubit_circuit)

    qubit_to_measure = list(single_measurement_circuit.qubits)[0]
    m_instruction = Instruction([qubit_to_measure], "M")

    m_instruction.is_measurement = True
    m_instruction.params = ()
    check = Check([Pauli(qubit_to_measure, PauliLetter('Z'))])
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

    m_instruction = Instruction([qubit_1, qubit_2], "M")

    m_instruction.params = ()
    check = Check([Pauli(qubit_1, PauliLetter('Z')),
                  Pauli(qubit_2, PauliLetter('Z'))])
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


def test_circuit_add_instruction_fails_if_noise_on_even_tick(
        mocker: MockerFixture):
    expected_error = "Can't place a noise instruction at an even tick"
    circuit = Circuit()
    tick = random.choice(range(-20, 20, 2))
    instruction = mocker.Mock(spec=Instruction)
    instruction.is_noise = True
    with pytest.raises(ValueError, match=expected_error):
        circuit.add_instruction(tick, instruction)


def test_circuit_add_instruction_fails_if_non_noise_on_odd_tick(
        mocker: MockerFixture):
    expected_error = "Can't place a non-noise instruction at an odd tick"
    circuit = Circuit()
    tick = random.choice(range(-25, 25, 2))
    instruction = mocker.Mock(spec=Instruction)
    instruction.is_noise = False
    with pytest.raises(ValueError, match=expected_error):
        circuit.add_instruction(tick, instruction)


def test_circuit_add_instruction_fails_if_conflicting_instructions(
        mocker: MockerFixture):
    expected_error = "Tried to compile conflicting instructions"
    circuit = Circuit()
    tick = random.choice(range(-20, 20, 2))
    qubit = mocker.Mock(spec=Qubit)

    instruction = Instruction([qubit], 'Some instruction')
    conflicting_instruction = Instruction([qubit], 'Some other instruction')

    circuit.instructions = {tick: {qubit: [instruction]}}
    with pytest.raises(ValueError, match=expected_error):
        circuit.add_instruction(tick, conflicting_instruction)


def test_circuit_add_instruction_succeeds_otherwise(
        mocker: MockerFixture):
    circuit = Circuit()
    tick = random.choice(range(-20, 20, 2))
    qubit = mocker.Mock(spec=Qubit)
    instruction = Instruction([qubit], 'Some instruction')
    circuit.add_instruction(tick, instruction)
    assert circuit.instructions[tick][qubit] == [instruction]


def test_circuit_add_repeat_block_fails_if_block_empty():
    expected_error = "Repeat block must contain at least one tick"
    circuit = Circuit()
    start = random.randint(-100, 100)
    end = random.randint(start - 100, start)
    repeats = random.randint(1, 100)
    with pytest.raises(ValueError, match=expected_error):
        circuit.add_repeat_block(start, end, repeats)


def test_circuit_add_repeat_block_fails_if_repeats_less_than_once():
    expected_error = "Repeat block must repeat at least once"
    circuit = Circuit()
    start = random.randint(-100, 100)
    end = random.randint(start + 1, start + 100)
    repeats = random.randint(-100, 0)
    with pytest.raises(ValueError, match=expected_error):
        circuit.add_repeat_block(start, end, repeats)


def test_circuit_add_repeat_block_fails_if_conflicts_with_existing_repeat_block(
        mocker: MockerFixture):
    expected_error = "Can't compile conflicting repeat blocks"
    circuit = Circuit()
    start = random.randint(-100, 100)
    end = random.randint(start + 1, start + 100)
    repeats = random.randint(1, 100)

    # Add some existing repeat blocks to ticks in [start, end).
    width = end - start
    k = random.randint(1, width)
    ticks = random.sample(range(start, end), k)
    for tick in ticks:
        circuit.repeat_blocks[tick] = mocker.Mock(spec=RepeatBlock)

    # Now try to compile the new repeat block.
    with pytest.raises(ValueError, match=expected_error):
        circuit.add_repeat_block(start, end, repeats)


def test_circuit_add_repeat_block_succeeds_otherwise():
    circuit = Circuit()
    start = random.randint(-100, 100)
    end = random.randint(start + 1, start + 100)
    repeats = random.randint(1, 100)
    circuit.add_repeat_block(start, end, repeats)
    for tick in range(start, end):
        assert circuit.repeat_blocks[tick] == (start, end, repeats)


def test_to_stim(capfd):
    single_qubit_circuit.to_stim(None, None, track_progress=False)
    out, _ = capfd.readouterr()
    assert out == ""


def test__to_stim():
    circuit = single_qubit_circuit._to_stim(None, None, True, None)
    assert stim.Circuit(str(circuit)) == stim.Circuit(
        """QUBIT_COORDS(1) 0
            R 0
            TICK
            Z 0"""
    )

    circuit = circuit_with_two_gates_on_same_qubit._to_stim(
        None, None, True, None)

    assert stim.Circuit(str(circuit)) == stim.Circuit(
        """
        QUBIT_COORDS(1) 0
        R 0
        TICK
        PAULI_CHANNEL_1(0.1, 0.1, 0.1) 0
        PAULI_CHANNEL_1(0.2, 0.2, 0.2) 0
    """)
    rsc_circuit_one_layer = create_rsc_circuit()
    stim_rsc_circuit_one_layer = rsc_circuit_one_layer._to_stim(
        None, None, True, None)

    # testing if the properties of the measurer class are reset
    assert rsc_circuit_one_layer.measurer.measurement_numbers == {}
    assert rsc_circuit_one_layer.measurer.detectors_compiled == defaultdict(
        bool)
    assert rsc_circuit_one_layer.measurer.total_measurements == 0

    # test number of measurements
    assert stim_rsc_circuit_one_layer.num_measurements == 17
    assert stim_rsc_circuit_one_layer.num_detectors == 8


def test_add_idling_noise():
    single_qubit_circuit.add_idling_noise(None, None)
    n_idling_gates = single_qubit_circuit.number_of_instructions(
        "PAULI_CHANNEL_I"
    )
    assert n_idling_gates == 0

    two_qubit_circuit.add_idling_noise(OneQubitNoise(0.1, 0.1, 0.1), None)
    n_idling_errors = two_qubit_circuit.number_of_instructions(
        "PAULI_CHANNEL_1"
    )
    assert n_idling_errors == 1

    circ_w_res_idle = deepcopy(circuit_with_resonator_idle)
    circ_w_res_idle.add_idling_noise(
        None, OneQubitNoise(0.2, 0.2, 0.2))
    n_idling_errors = circ_w_res_idle.number_of_instructions(
        "PAULI_CHANNEL_1"
    )

    assert n_idling_errors == 1

    n_idling_errors = circuit_with_resonator_idle.add_idling_noise(
        OneQubitNoise(0.1, 0.1, 0.1), OneQubitNoise(0.2, 0.2, 0.2))
    n_idling_errors = circuit_with_resonator_idle.number_of_instructions(
        "PAULI_CHANNEL_1")

    assert n_idling_errors == 3


def test_circuit_add_idling_noise_does_not_add_idling_noise_after_identity_gate(
        mocker: MockerFixture):
    circuit = Circuit()
    qubit = mocker.Mock(spec=Qubit)
    identity = Instruction([qubit], 'I')
    circuit.instructions = {0: {qubit: [identity]}}
    circuit.add_idling_noise(OneQubitNoise.uniform(0.1), None)
    # Assert that nothing has happened!
    assert circuit.instructions == {0: {qubit: [identity]}}


def test_circuit_get_idle_qubits(mocker: MockerFixture):
    circuit = Circuit()
    qubits = [mocker.Mock(spec=Qubit) for _ in range(4)]
    circuit.qubits = set(qubits)
    # Only initialise the last three qubits, so qubit 0 shouldn't be idle.
    circuit.init_ticks = defaultdict(list)
    for qubit in qubits[1:]:
        circuit.init_ticks[qubit].append(0)
    # Let only qubit 1 have non-trivial instructions, so this qubit also
    # shouldn't be idle.
    circuit.instructions = {0: {
        qubits[0]: [Instruction([qubits[0]], 'I')],
        qubits[1]: [Instruction([qubits[1]], 'X')],
        qubits[2]: [Instruction([qubits[2]], 'I')],
        qubits[3]: []}}

    idle_qubits = circuit.get_idle_qubits(0)
    # Only the last two qubits should be idle.
    assert idle_qubits == set(qubits[2:])


def test_circuit_entered_repeat_block():
    circuit = Circuit()
    circuit.repeat_blocks = {
        0: None,
        1: (1, 2, 10),
        2: (2, 4, 10),
        3: (2, 4, 10),
        4: None}
    for i in [1, 2]:
        tick = i
        last_tick = i-1
        assert circuit.entered_repeat_block(tick, last_tick)
    for i in [3, 4]:
        tick = i
        last_tick = i-1
        assert not circuit.entered_repeat_block(tick, last_tick)


def test_circuit_left_repeat_block():
    circuit = Circuit()
    circuit.repeat_blocks = {
        0: None,
        1: (1, 2, 10),
        2: (2, 4, 10),
        3: (2, 4, 10),
        4: None}
    for i in [1, 3]:
        tick = i
        last_tick = i - 1
        assert circuit.left_repeat_block(tick, last_tick) is None
    for i in [2, 4]:
        tick = i
        last_tick = i - 1
        assert circuit.left_repeat_block(tick, last_tick) == 10

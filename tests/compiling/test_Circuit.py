import stim
from main.building_blocks.Qubit import Qubit
from main.compiling.Circuit import Circuit
from main.compiling.Instruction import Instruction
from main.compiling.noise.models.CircuitLevelNoise import CircuitLevelNoise
from main.compiling.noise.models.NoNoise import NoNoise

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


def test_get_number_of_specific_gates():
    n_R_gates = single_qubit_circuit.get_number_of_occurences_of_gate("R")
    assert n_R_gates == 1

    n_X_gates = single_qubit_circuit.get_number_of_occurences_of_gate("X")
    assert n_X_gates == 0


def test_to_stim(capfd):

    single_qubit_circuit.to_stim(NoNoise(), track_progress=False)
    out, _ = capfd.readouterr()
    assert out == ""

    # test that a progress bar is created
    single_qubit_circuit.to_stim(NoNoise())
    out, _ = capfd.readouterr()
    assert out != ""


def test__to_stim():
    circuit = single_qubit_circuit._to_stim(NoNoise(), True, None)
    print(str(circuit))
    assert stim.Circuit(str(circuit)) == stim.Circuit(
        """QUBIT_COORDS(1) 0
            R 0
                      TICK
                      Z 0"""
    )


def test___repr__():
    assert single_qubit_circuit.__repr__() == "1: ───R───Z───"


def add_idling_noise():
    # test if no noise is added
    single_qubit_circuit.add_idle_noise(CircuitLevelNoise(0, 1.0, 0, 0, 0))
    n_idling_gates = single_qubit_circuit.get_number_of_occurences_of_gate("I")
    assert n_idling_gates == 0

    two_qubit_circuit.add_idle_noise(CircuitLevelNoise(0, 1.0, 0, 0, 0))
    n_idling_errors = two_qubit_circuit.get_number_of_occurences_of_gate(
        "PAULI_CHANNEL_1"
    )
    assert n_idling_errors == 1

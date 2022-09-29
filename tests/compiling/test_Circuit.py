from collections import defaultdict
import copy
import pytest
import stim
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.compiling.Circuit import Circuit
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

    rsc_finals = [Pauli(qubit, PauliZ) for qubit in rsc_qubits]
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


def test_get_number_of_occurences_gates():
    n_R_gates = single_qubit_circuit.get_number_of_occurrences_of_gate("R")
    assert n_R_gates == 1

    n_X_gates = single_qubit_circuit.get_number_of_occurrences_of_gate("X")
    assert n_X_gates == 0


def test_to_stim(capfd):
    single_qubit_circuit.to_stim(None, track_progress=False)
    out, _ = capfd.readouterr()
    assert out == ""

    single_qubit_circuit.to_stim(None)
    out, _ = capfd.readouterr()
    assert out != ""


def test__to_stim():
    circuit = single_qubit_circuit._to_stim(None, True, None)
    assert stim.Circuit(str(circuit)) == stim.Circuit(
        """QUBIT_COORDS(1) 0
            R 0
            TICK
            Z 0"""
    )

    rsc_circuit_one_layer = create_rsc_circuit()
    stim_rsc_circuit_one_layer = rsc_circuit_one_layer._to_stim(None, True, None)

    # testing if the properties of the measurer class are reset
    assert rsc_circuit_one_layer.measurer.measurement_numbers == {}
    assert rsc_circuit_one_layer.measurer.detectors_built == defaultdict(bool)
    assert rsc_circuit_one_layer.measurer.total_measurements == 0

    # test number of measurements
    assert stim_rsc_circuit_one_layer.num_measurements == 17
    assert stim_rsc_circuit_one_layer.num_detectors == 8


def test_to_circ_string():
    assert single_qubit_circuit.to_cirq_string() == "1: ───R───Z───"


def add_iddle_noise():
    # test if no noise is added
    single_qubit_circuit.add_idling_noise(None)
    n_idling_gates = single_qubit_circuit.get_number_of_occurrences_of_gate(
        "PAULI_CHANNEL_I"
    )
    assert n_idling_gates == 0

    two_qubit_circuit.add_idling_noise(OneQubitNoise(0.1, 0.1, 0.1))
    n_idling_errors = two_qubit_circuit.get_number_of_occurrences_of_gate(
        "PAULI_CHANNEL_1"
    )
    assert n_idling_errors == 1

from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.RepetitionCode import RepetitionCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models import PhenomenologicalNoise, CircuitLevelNoise
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CnotExtractor import CnotExtractor
from main.utils.enums import State


def test_repetition_code_end_to_end_1():
    """
    Distance: 3
    Noise model: None
    Syndrome extractor: CnotExtractor
    Compiler: AncillaPerCheckCompiler
    total_rounds: 3
    Initial States: all Zero
    Final measurements: all Z
    Observables: logical Z
    """
    code = RepetitionCode(distance=3)
    extractor = CnotExtractor()
    compiler = AncillaPerCheckCompiler(syndrome_extractor=extractor)

    data_qubits = code.data_qubits.values()
    initial_states = {qubit: State.Zero for qubit in data_qubits}
    final_measurements = [
        Pauli(qubit, PauliLetter('Z')) for qubit in data_qubits]
    stim_circuit = compiler.compile_to_stim(
        code=code,
        total_rounds=3,
        initial_states=initial_states,
        final_measurements=final_measurements,
        observables=[code.logical_qubits[0].z])

    expected = """QUBIT_COORDS(0) 0
QUBIT_COORDS(1) 1
QUBIT_COORDS(2) 2
QUBIT_COORDS(3) 3
QUBIT_COORDS(4) 4
R 0 2 4
TICK
R 1 3
TICK
CX 0 1 2 3
TICK
CX 2 1 4 3
TICK
M 1 3
DETECTOR(1, 0) rec[-2]
DETECTOR(3, 0) rec[-1]
SHIFT_COORDS(0, 1)
TICK
R 1 3
TICK
CX 0 1 2 3
TICK
CX 2 1 4 3
TICK
M 1 3
DETECTOR(1, 0) rec[-4] rec[-2]
DETECTOR(3, 0) rec[-3] rec[-1]
SHIFT_COORDS(0, 1)
TICK
R 1 3
TICK
CX 0 1 2 3
TICK
CX 2 1 4 3
TICK
M 1 3
DETECTOR(1, 0) rec[-4] rec[-2]
DETECTOR(3, 0) rec[-3] rec[-1]
SHIFT_COORDS(0, 1)
TICK
M 0 2 4
DETECTOR(1, 0) rec[-5] rec[-3] rec[-2]
DETECTOR(3, 0) rec[-4] rec[-2] rec[-1]
OBSERVABLE_INCLUDE(0) rec[-3]"""

    assert str(stim_circuit) == expected


def test_repetition_code_end_to_end_2():
    """
    Distance: 3
    Noise model: None
    Syndrome extractor: CnotExtractor
    Compiler: AncillaPerCheckCompiler
    total_rounds: 3
    Initial States: all Plus
    Final measurements: all X
    Observables: logical X
    """
    code = RepetitionCode(distance=3)
    extractor = CnotExtractor()
    compiler = AncillaPerCheckCompiler(syndrome_extractor=extractor)

    data_qubits = code.data_qubits.values()
    initial_states = {qubit: State.Plus for qubit in data_qubits}
    final_measurements = [
        Pauli(qubit, PauliLetter('X')) for qubit in data_qubits]
    stim_circuit = compiler.compile_to_stim(
        code=code,
        total_rounds=3,
        initial_states=initial_states,
        final_measurements=final_measurements,
        observables=[code.logical_qubits[0].x])

    expected = """QUBIT_COORDS(0) 0
QUBIT_COORDS(1) 1
QUBIT_COORDS(2) 2
QUBIT_COORDS(3) 3
QUBIT_COORDS(4) 4
RX 0 2 4
TICK
R 1 3
TICK
CX 0 1 2 3
TICK
CX 2 1 4 3
TICK
M 1 3
SHIFT_COORDS(0, 1)
TICK
R 1 3
TICK
CX 0 1 2 3
TICK
CX 2 1 4 3
TICK
M 1 3
DETECTOR(1, 0) rec[-4] rec[-2]
DETECTOR(3, 0) rec[-3] rec[-1]
SHIFT_COORDS(0, 1)
TICK
R 1 3
TICK
CX 0 1 2 3
TICK
CX 2 1 4 3
TICK
M 1 3
DETECTOR(1, 0) rec[-4] rec[-2]
DETECTOR(3, 0) rec[-3] rec[-1]
SHIFT_COORDS(0, 1)
TICK
MX 0 2 4
OBSERVABLE_INCLUDE(0) rec[-3] rec[-2] rec[-1]"""

    assert str(stim_circuit) == expected


def test_repetition_code_end_to_end_3():
    """
    Distance: 3
    Noise model: Phenomenological
    Syndrome extractor: CnotExtractor
    Compiler: AncillaPerCheckCompiler
    total_rounds: 3
    Initial States: all Zero
    Final measurements: all Z
    Observables: logical Z
    """
    code = RepetitionCode(distance=3)
    extractor = CnotExtractor()
    compiler = AncillaPerCheckCompiler(
        noise_model=PhenomenologicalNoise(0.1, 0.2),
        syndrome_extractor=extractor)

    data_qubits = code.data_qubits.values()
    initial_states = {qubit: State.Zero for qubit in data_qubits}
    final_measurements = [
        Pauli(qubit, PauliLetter('Z')) for qubit in data_qubits]
    stim_circuit = compiler.compile_to_stim(
        code=code,
        total_rounds=3,
        initial_states=initial_states,
        final_measurements=final_measurements,
        observables=[code.logical_qubits[0].z])
    expected = """QUBIT_COORDS(0) 0
QUBIT_COORDS(1) 1
QUBIT_COORDS(2) 2
QUBIT_COORDS(3) 3
QUBIT_COORDS(4) 4
R 0 2 4
TICK
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 0 2 4
TICK
R 1 3
TICK
CX 0 1 2 3
TICK
CX 2 1 4 3
TICK
M(0.2) 1 3
DETECTOR(1, 0) rec[-2]
DETECTOR(3, 0) rec[-1]
SHIFT_COORDS(0, 1)
TICK
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 0 2 4
TICK
R 1 3
TICK
CX 0 1 2 3
TICK
CX 2 1 4 3
TICK
M(0.2) 1 3
DETECTOR(1, 0) rec[-4] rec[-2]
DETECTOR(3, 0) rec[-3] rec[-1]
SHIFT_COORDS(0, 1)
TICK
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 0 2 4
TICK
R 1 3
TICK
CX 0 1 2 3
TICK
CX 2 1 4 3
TICK
M(0.2) 1 3
DETECTOR(1, 0) rec[-4] rec[-2]
DETECTOR(3, 0) rec[-3] rec[-1]
SHIFT_COORDS(0, 1)
TICK
M(0.2) 0 2 4
DETECTOR(1, 0) rec[-5] rec[-3] rec[-2]
DETECTOR(3, 0) rec[-4] rec[-2] rec[-1]
OBSERVABLE_INCLUDE(0) rec[-3]"""

    assert str(stim_circuit) == expected


def test_repetition_code_end_to_end_4():
    """
    Distance: 3
    Noise model: CircuitLevel
    Syndrome extractor: CnotExtractor
    Compiler: AncillaPerCheckCompiler
    total_rounds: 3
    Initial States: all Zero
    Final measurements: all Z
    Observables: logical Z
    """
    code = RepetitionCode(distance=3)
    extractor = CnotExtractor()
    compiler = AncillaPerCheckCompiler(
        noise_model=CircuitLevelNoise(0.1, 0.2, 0.3, 0.4, 0.5),
        syndrome_extractor=extractor)

    data_qubits = code.data_qubits.values()
    initial_states = {qubit: State.Zero for qubit in data_qubits}
    final_measurements = [
        Pauli(qubit, PauliLetter('Z')) for qubit in data_qubits]
    stim_circuit = compiler.compile_to_stim(
        code=code,
        total_rounds=3,
        initial_states=initial_states,
        final_measurements=final_measurements,
        observables=[code.logical_qubits[0].z])

    expected = """QUBIT_COORDS(0) 0
QUBIT_COORDS(1) 1
QUBIT_COORDS(2) 2
QUBIT_COORDS(3) 3
QUBIT_COORDS(4) 4
R 0 2 4
TICK
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 0 2 4
TICK
R 1 3
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 2 4
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 1 3
TICK
CX 0 1 2 3
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 4
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 0 1 2 3
TICK
CX 2 1 4 3
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 2 1 4 3
TICK
M(0.5) 1 3
DETECTOR(1, 0) rec[-2]
DETECTOR(3, 0) rec[-1]
SHIFT_COORDS(0, 1)
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 2 4
TICK
R 1 3
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 2 4
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 1 3
TICK
CX 0 1 2 3
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 4
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 0 1 2 3
TICK
CX 2 1 4 3
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 2 1 4 3
TICK
M(0.5) 1 3
DETECTOR(1, 0) rec[-4] rec[-2]
DETECTOR(3, 0) rec[-3] rec[-1]
SHIFT_COORDS(0, 1)
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 2 4
TICK
R 1 3
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 2 4
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 1 3
TICK
CX 0 1 2 3
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 4
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 0 1 2 3
TICK
CX 2 1 4 3
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 2 1 4 3
TICK
M(0.5) 1 3
DETECTOR(1, 0) rec[-4] rec[-2]
DETECTOR(3, 0) rec[-3] rec[-1]
SHIFT_COORDS(0, 1)
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 2 4
TICK
M(0.5) 0 2 4
DETECTOR(1, 0) rec[-5] rec[-3] rec[-2]
DETECTOR(3, 0) rec[-4] rec[-2] rec[-1]
OBSERVABLE_INCLUDE(0) rec[-3]"""
    assert str(stim_circuit) == expected
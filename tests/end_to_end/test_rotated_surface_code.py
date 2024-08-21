from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models import PhenomenologicalNoise, CircuitLevelNoise
from main.compiling.syndrome_extraction.controlled_gate_orderers.RotatedSurfaceCodeOrderer import \
    RotatedSurfaceCodeOrderer
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CnotExtractor import CnotExtractor
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CzExtractor import CzExtractor
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.pure.CnotCssExtractor import CnotCssExtractor
from main.utils.enums import State


def test_rotated_surface_code_compilation_end_to_end_1():
    """
    Distance: 3
    Noise model: None
    Syndrome extractor: CnotCssExtractor
    Compiler: AncillaPerCheckCompiler
    total_rounds: 3
    Initial States: all Zero
    Final measurements: all Z
    Observables: logical Z
    """
    code = RotatedSurfaceCode(distance=3)
    extractor = CnotCssExtractor(RotatedSurfaceCodeOrderer())
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

    expected = """QUBIT_COORDS(0, 2) 0
QUBIT_COORDS(0, 3) 1
QUBIT_COORDS(1, 0) 2
QUBIT_COORDS(1, 1) 3
QUBIT_COORDS(1, 2) 4
QUBIT_COORDS(1, 3) 5
QUBIT_COORDS(2, 0) 6
QUBIT_COORDS(2, 1) 7
QUBIT_COORDS(2, 2) 8
QUBIT_COORDS(2, 3) 9
QUBIT_COORDS(2, 4) 10
QUBIT_COORDS(3, 1) 11
QUBIT_COORDS(3, 2) 12
QUBIT_COORDS(3, 3) 13
QUBIT_COORDS(3, 4) 14
QUBIT_COORDS(4, 1) 15
QUBIT_COORDS(4, 2) 16
R 0 3 6 5 8 11 10 13 16
TICK
R 4
RX 7 9
R 12 2 14
RX 1 15
TICK
CX 8 4 7 11 9 13 16 12 6 2 1 5
TICK
CX 5 4 7 6 9 8 13 12 3 2 1 0
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
M 4
MX 7 9
M 12 2 14
MX 1 15
DETECTOR(1, 2, 0) rec[-8]
DETECTOR(3, 2, 0) rec[-5]
DETECTOR(1, 0, 0) rec[-4]
DETECTOR(3, 4, 0) rec[-3]
SHIFT_COORDS(0, 0, 1)
TICK
R 4
RX 7 9
R 12 2 14
RX 1 15
TICK
CX 8 4 7 11 9 13 16 12 6 2 1 5
TICK
CX 5 4 7 6 9 8 13 12 3 2 1 0
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
M 4
MX 7 9
M 12 2 14
MX 1 15
DETECTOR(1, 2, 0) rec[-16] rec[-8]
DETECTOR(2, 1, 0) rec[-15] rec[-7]
DETECTOR(2, 3, 0) rec[-14] rec[-6]
DETECTOR(3, 2, 0) rec[-13] rec[-5]
DETECTOR(1, 0, 0) rec[-12] rec[-4]
DETECTOR(3, 4, 0) rec[-11] rec[-3]
DETECTOR(0, 3, 0) rec[-10] rec[-2]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
R 4
RX 7 9
R 12 2 14
RX 1 15
TICK
CX 8 4 7 11 9 13 16 12 6 2 1 5
TICK
CX 5 4 7 6 9 8 13 12 3 2 1 0
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
M 4
MX 7 9
M 12 2 14
MX 1 15
DETECTOR(1, 2, 0) rec[-16] rec[-8]
DETECTOR(2, 1, 0) rec[-15] rec[-7]
DETECTOR(2, 3, 0) rec[-14] rec[-6]
DETECTOR(3, 2, 0) rec[-13] rec[-5]
DETECTOR(1, 0, 0) rec[-12] rec[-4]
DETECTOR(3, 4, 0) rec[-11] rec[-3]
DETECTOR(0, 3, 0) rec[-10] rec[-2]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
M 0 3 6 5 8 11 10 13 16
DETECTOR(1, 0, 0) rec[-13] rec[-8] rec[-7]
DETECTOR(1, 2, 0) rec[-17] rec[-9] rec[-8] rec[-6] rec[-5]
DETECTOR(3, 4, 0) rec[-12] rec[-3] rec[-2]
DETECTOR(3, 2, 0) rec[-14] rec[-5] rec[-4] rec[-2] rec[-1]
OBSERVABLE_INCLUDE(0) rec[-9] rec[-6] rec[-3]"""

    assert str(stim_circuit) == expected


def test_rotated_surface_code_compilation_end_to_end_2():
    """
    Distance: 3
    Noise model: None
    Syndrome extractor: CnotCssExtractor
    Compiler: AncillaPerCheckCompiler
    total_rounds: 3
    Initial States: all Plus
    Final measurements: all X
    Observables: logical X
    """
    code = RotatedSurfaceCode(distance=3)
    extractor = CnotCssExtractor(RotatedSurfaceCodeOrderer())
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

    expected = """QUBIT_COORDS(0, 2) 0
QUBIT_COORDS(0, 3) 1
QUBIT_COORDS(1, 0) 2
QUBIT_COORDS(1, 1) 3
QUBIT_COORDS(1, 2) 4
QUBIT_COORDS(1, 3) 5
QUBIT_COORDS(2, 0) 6
QUBIT_COORDS(2, 1) 7
QUBIT_COORDS(2, 2) 8
QUBIT_COORDS(2, 3) 9
QUBIT_COORDS(2, 4) 10
QUBIT_COORDS(3, 1) 11
QUBIT_COORDS(3, 2) 12
QUBIT_COORDS(3, 3) 13
QUBIT_COORDS(3, 4) 14
QUBIT_COORDS(4, 1) 15
QUBIT_COORDS(4, 2) 16
RX 0 3 6 5 8 11 10 13 16
TICK
R 4
RX 7 9
R 12 2 14
RX 1 15
TICK
CX 8 4 7 11 9 13 16 12 6 2 1 5
TICK
CX 5 4 7 6 9 8 13 12 3 2 1 0
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
M 4
MX 7 9
M 12 2 14
MX 1 15
DETECTOR(2, 1, 0) rec[-7]
DETECTOR(2, 3, 0) rec[-6]
DETECTOR(0, 3, 0) rec[-2]
DETECTOR(4, 1, 0) rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
R 4
RX 7 9
R 12 2 14
RX 1 15
TICK
CX 8 4 7 11 9 13 16 12 6 2 1 5
TICK
CX 5 4 7 6 9 8 13 12 3 2 1 0
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
M 4
MX 7 9
M 12 2 14
MX 1 15
DETECTOR(1, 2, 0) rec[-16] rec[-8]
DETECTOR(2, 1, 0) rec[-15] rec[-7]
DETECTOR(2, 3, 0) rec[-14] rec[-6]
DETECTOR(3, 2, 0) rec[-13] rec[-5]
DETECTOR(1, 0, 0) rec[-12] rec[-4]
DETECTOR(3, 4, 0) rec[-11] rec[-3]
DETECTOR(0, 3, 0) rec[-10] rec[-2]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
R 4
RX 7 9
R 12 2 14
RX 1 15
TICK
CX 8 4 7 11 9 13 16 12 6 2 1 5
TICK
CX 5 4 7 6 9 8 13 12 3 2 1 0
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
M 4
MX 7 9
M 12 2 14
MX 1 15
DETECTOR(1, 2, 0) rec[-16] rec[-8]
DETECTOR(2, 1, 0) rec[-15] rec[-7]
DETECTOR(2, 3, 0) rec[-14] rec[-6]
DETECTOR(3, 2, 0) rec[-13] rec[-5]
DETECTOR(1, 0, 0) rec[-12] rec[-4]
DETECTOR(3, 4, 0) rec[-11] rec[-3]
DETECTOR(0, 3, 0) rec[-10] rec[-2]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
MX 0 3 6 5 8 11 10 13 16
DETECTOR(0, 3, 0) rec[-11] rec[-9] rec[-6]
DETECTOR(2, 1, 0) rec[-16] rec[-8] rec[-7] rec[-5] rec[-4]
DETECTOR(2, 3, 0) rec[-15] rec[-6] rec[-5] rec[-3] rec[-2]
DETECTOR(4, 1, 0) rec[-10] rec[-4] rec[-1]
OBSERVABLE_INCLUDE(0) rec[-9] rec[-8] rec[-7]"""

    assert str(stim_circuit) == expected


def test_rotated_surface_code_compilation_end_to_end_3():
    """
    Distance: 3
    Noise model: Phenomenological
    Syndrome extractor: CnotCssExtractor
    Compiler: AncillaPerCheckCompiler
    total_rounds: 3
    Initial States: all Zero
    Final measurements: all Z
    Observables: logical Z
    """
    code = RotatedSurfaceCode(distance=3)
    extractor = CnotCssExtractor(RotatedSurfaceCodeOrderer())
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

    expected = """QUBIT_COORDS(0, 2) 0
QUBIT_COORDS(0, 3) 1
QUBIT_COORDS(1, 0) 2
QUBIT_COORDS(1, 1) 3
QUBIT_COORDS(1, 2) 4
QUBIT_COORDS(1, 3) 5
QUBIT_COORDS(2, 0) 6
QUBIT_COORDS(2, 1) 7
QUBIT_COORDS(2, 2) 8
QUBIT_COORDS(2, 3) 9
QUBIT_COORDS(2, 4) 10
QUBIT_COORDS(3, 1) 11
QUBIT_COORDS(3, 2) 12
QUBIT_COORDS(3, 3) 13
QUBIT_COORDS(3, 4) 14
QUBIT_COORDS(4, 1) 15
QUBIT_COORDS(4, 2) 16
R 0 3 6 5 8 11 10 13 16
TICK
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 0 3 6 5 8 11 10 13 16
TICK
R 4
RX 7 9
R 12 2 14
RX 1 15
TICK
CX 8 4 7 11 9 13 16 12 6 2 1 5
TICK
CX 5 4 7 6 9 8 13 12 3 2 1 0
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
M(0.2) 4
MX(0.2) 7 9
M(0.2) 12 2 14
MX(0.2) 1 15
DETECTOR(1, 2, 0) rec[-8]
DETECTOR(3, 2, 0) rec[-5]
DETECTOR(1, 0, 0) rec[-4]
DETECTOR(3, 4, 0) rec[-3]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 0 3 6 5 8 11 10 13 16
TICK
R 4
RX 7 9
R 12 2 14
RX 1 15
TICK
CX 8 4 7 11 9 13 16 12 6 2 1 5
TICK
CX 5 4 7 6 9 8 13 12 3 2 1 0
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
M(0.2) 4
MX(0.2) 7 9
M(0.2) 12 2 14
MX(0.2) 1 15
DETECTOR(1, 2, 0) rec[-16] rec[-8]
DETECTOR(2, 1, 0) rec[-15] rec[-7]
DETECTOR(2, 3, 0) rec[-14] rec[-6]
DETECTOR(3, 2, 0) rec[-13] rec[-5]
DETECTOR(1, 0, 0) rec[-12] rec[-4]
DETECTOR(3, 4, 0) rec[-11] rec[-3]
DETECTOR(0, 3, 0) rec[-10] rec[-2]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 0 3 6 5 8 11 10 13 16
TICK
R 4
RX 7 9
R 12 2 14
RX 1 15
TICK
CX 8 4 7 11 9 13 16 12 6 2 1 5
TICK
CX 5 4 7 6 9 8 13 12 3 2 1 0
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
M(0.2) 4
MX(0.2) 7 9
M(0.2) 12 2 14
MX(0.2) 1 15
DETECTOR(1, 2, 0) rec[-16] rec[-8]
DETECTOR(2, 1, 0) rec[-15] rec[-7]
DETECTOR(2, 3, 0) rec[-14] rec[-6]
DETECTOR(3, 2, 0) rec[-13] rec[-5]
DETECTOR(1, 0, 0) rec[-12] rec[-4]
DETECTOR(3, 4, 0) rec[-11] rec[-3]
DETECTOR(0, 3, 0) rec[-10] rec[-2]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
M(0.2) 0 3 6 5 8 11 10 13 16
DETECTOR(1, 0, 0) rec[-13] rec[-8] rec[-7]
DETECTOR(1, 2, 0) rec[-17] rec[-9] rec[-8] rec[-6] rec[-5]
DETECTOR(3, 4, 0) rec[-12] rec[-3] rec[-2]
DETECTOR(3, 2, 0) rec[-14] rec[-5] rec[-4] rec[-2] rec[-1]
OBSERVABLE_INCLUDE(0) rec[-9] rec[-6] rec[-3]"""

    assert str(stim_circuit) == expected


def test_rotated_surface_code_compilation_end_to_end_4():
    """
    Distance: 3
    Noise model: CircuitLevel
    Syndrome extractor: CnotCssExtractor
    Compiler: AncillaPerCheckCompiler
    total_rounds: 3
    Initial States: all Zero
    Final measurements: all Z
    Observables: logical Z
    """
    code = RotatedSurfaceCode(distance=3)
    extractor = CnotCssExtractor(RotatedSurfaceCodeOrderer())
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

    expected = """QUBIT_COORDS(0, 2) 0
QUBIT_COORDS(0, 3) 1
QUBIT_COORDS(1, 0) 2
QUBIT_COORDS(1, 1) 3
QUBIT_COORDS(1, 2) 4
QUBIT_COORDS(1, 3) 5
QUBIT_COORDS(2, 0) 6
QUBIT_COORDS(2, 1) 7
QUBIT_COORDS(2, 2) 8
QUBIT_COORDS(2, 3) 9
QUBIT_COORDS(2, 4) 10
QUBIT_COORDS(3, 1) 11
QUBIT_COORDS(3, 2) 12
QUBIT_COORDS(3, 3) 13
QUBIT_COORDS(3, 4) 14
QUBIT_COORDS(4, 1) 15
QUBIT_COORDS(4, 2) 16
R 0 3 6 5 8 11 10 13 16
TICK
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 0 3 6 5 8 11 10 13 16
TICK
R 4
RX 7 9
R 12 2 14
RX 1 15
TICK
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 4 7 9 12 2 14 1 15
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 3 5 6 8 10 11 13 16
TICK
CX 8 4 7 11 9 13 16 12 6 2 1 5
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 8 4 7 11 9 13 16 12 6 2 1 5
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 3 10 14 15
TICK
CX 5 4 7 6 9 8 13 12 3 2 1 0
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 5 4 7 6 9 8 13 12 3 2 1 0
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 10 11 14 15 16
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 3 4 7 8 9 10 11 12 13 14 15 16
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 1 2 5 6
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 0 4 7 3 9 5 8 12 10 14 15 11
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 1 2 6 13 16
TICK
M(0.5) 4
MX(0.5) 7 9
M(0.5) 12 2 14
MX(0.5) 1 15
DETECTOR(1, 2, 0) rec[-8]
DETECTOR(3, 2, 0) rec[-5]
DETECTOR(1, 0, 0) rec[-4]
DETECTOR(3, 4, 0) rec[-3]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 3 5 6 8 10 11 13 16
TICK
R 4
RX 7 9
R 12 2 14
RX 1 15
TICK
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 4 7 9 12 2 14 1 15
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 3 5 6 8 10 11 13 16
TICK
CX 8 4 7 11 9 13 16 12 6 2 1 5
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 8 4 7 11 9 13 16 12 6 2 1 5
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 3 10 14 15
TICK
CX 5 4 7 6 9 8 13 12 3 2 1 0
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 5 4 7 6 9 8 13 12 3 2 1 0
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 10 11 14 15 16
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 3 4 7 8 9 10 11 12 13 14 15 16
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 1 2 5 6
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 0 4 7 3 9 5 8 12 10 14 15 11
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 1 2 6 13 16
TICK
M(0.5) 4
MX(0.5) 7 9
M(0.5) 12 2 14
MX(0.5) 1 15
DETECTOR(1, 2, 0) rec[-16] rec[-8]
DETECTOR(2, 1, 0) rec[-15] rec[-7]
DETECTOR(2, 3, 0) rec[-14] rec[-6]
DETECTOR(3, 2, 0) rec[-13] rec[-5]
DETECTOR(1, 0, 0) rec[-12] rec[-4]
DETECTOR(3, 4, 0) rec[-11] rec[-3]
DETECTOR(0, 3, 0) rec[-10] rec[-2]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 3 5 6 8 10 11 13 16
TICK
R 4
RX 7 9
R 12 2 14
RX 1 15
TICK
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 4 7 9 12 2 14 1 15
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 3 5 6 8 10 11 13 16
TICK
CX 8 4 7 11 9 13 16 12 6 2 1 5
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 8 4 7 11 9 13 16 12 6 2 1 5
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 3 10 14 15
TICK
CX 5 4 7 6 9 8 13 12 3 2 1 0
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 5 4 7 6 9 8 13 12 3 2 1 0
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 10 11 14 15 16
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 3 4 7 8 9 10 11 12 13 14 15 16
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 1 2 5 6
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 0 4 7 3 9 5 8 12 10 14 15 11
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 1 2 6 13 16
TICK
M(0.5) 4
MX(0.5) 7 9
M(0.5) 12 2 14
MX(0.5) 1 15
DETECTOR(1, 2, 0) rec[-16] rec[-8]
DETECTOR(2, 1, 0) rec[-15] rec[-7]
DETECTOR(2, 3, 0) rec[-14] rec[-6]
DETECTOR(3, 2, 0) rec[-13] rec[-5]
DETECTOR(1, 0, 0) rec[-12] rec[-4]
DETECTOR(3, 4, 0) rec[-11] rec[-3]
DETECTOR(0, 3, 0) rec[-10] rec[-2]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 3 5 6 8 10 11 13 16
TICK
M(0.5) 0 3 6 5 8 11 10 13 16
DETECTOR(1, 0, 0) rec[-13] rec[-8] rec[-7]
DETECTOR(1, 2, 0) rec[-17] rec[-9] rec[-8] rec[-6] rec[-5]
DETECTOR(3, 4, 0) rec[-12] rec[-3] rec[-2]
DETECTOR(3, 2, 0) rec[-14] rec[-5] rec[-4] rec[-2] rec[-1]
OBSERVABLE_INCLUDE(0) rec[-9] rec[-6] rec[-3]"""

    assert str(stim_circuit) == expected


def test_rotated_surface_code_compilation_end_to_end_5():
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
    code = RotatedSurfaceCode(distance=3)
    extractor = CnotExtractor(RotatedSurfaceCodeOrderer())
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

    expected = """QUBIT_COORDS(0, 2) 0
QUBIT_COORDS(0, 3) 1
QUBIT_COORDS(1, 0) 2
QUBIT_COORDS(1, 1) 3
QUBIT_COORDS(1, 2) 4
QUBIT_COORDS(1, 3) 5
QUBIT_COORDS(2, 0) 6
QUBIT_COORDS(2, 1) 7
QUBIT_COORDS(2, 2) 8
QUBIT_COORDS(2, 3) 9
QUBIT_COORDS(2, 4) 10
QUBIT_COORDS(3, 1) 11
QUBIT_COORDS(3, 2) 12
QUBIT_COORDS(3, 3) 13
QUBIT_COORDS(3, 4) 14
QUBIT_COORDS(4, 1) 15
QUBIT_COORDS(4, 2) 16
R 0 3 6 5 8 11 10 13 16
TICK
R 4 7 9 12 2 14 1 15
TICK
H 11 13 5
TICK
CX 8 4 11 7 13 9 16 12 6 2 5 1
TICK
H 11 13 5
TICK
H 6 8 0
TICK
CX 5 4 6 7 8 9 13 12 3 2 0 1
TICK
H 6 8 0
TICK
H 8 10 16
TICK
CX 3 4 8 7 10 9 11 12 13 14 16 15
TICK
H 8 10 16
TICK
H 3 5 11
TICK
CX 0 4 3 7 5 9 8 12 10 14 11 15
TICK
H 3 5 11
TICK
M 4 7 9 12 2 14 1 15
DETECTOR(1, 2, 0) rec[-8]
DETECTOR(3, 2, 0) rec[-5]
DETECTOR(1, 0, 0) rec[-4]
DETECTOR(3, 4, 0) rec[-3]
SHIFT_COORDS(0, 0, 1)
TICK
R 4 7 9 12 2 14 1 15
TICK
H 11 13 5
TICK
CX 8 4 11 7 13 9 16 12 6 2 5 1
TICK
H 11 13 5
TICK
H 6 8 0
TICK
CX 5 4 6 7 8 9 13 12 3 2 0 1
TICK
H 6 8 0
TICK
H 8 10 16
TICK
CX 3 4 8 7 10 9 11 12 13 14 16 15
TICK
H 8 10 16
TICK
H 3 5 11
TICK
CX 0 4 3 7 5 9 8 12 10 14 11 15
TICK
H 3 5 11
TICK
M 4 7 9 12 2 14 1 15
DETECTOR(1, 2, 0) rec[-16] rec[-8]
DETECTOR(2, 1, 0) rec[-15] rec[-7]
DETECTOR(2, 3, 0) rec[-14] rec[-6]
DETECTOR(3, 2, 0) rec[-13] rec[-5]
DETECTOR(1, 0, 0) rec[-12] rec[-4]
DETECTOR(3, 4, 0) rec[-11] rec[-3]
DETECTOR(0, 3, 0) rec[-10] rec[-2]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
R 4 7 9 12 2 14 1 15
TICK
H 11 13 5
TICK
CX 8 4 11 7 13 9 16 12 6 2 5 1
TICK
H 11 13 5
TICK
H 6 8 0
TICK
CX 5 4 6 7 8 9 13 12 3 2 0 1
TICK
H 6 8 0
TICK
H 8 10 16
TICK
CX 3 4 8 7 10 9 11 12 13 14 16 15
TICK
H 8 10 16
TICK
H 3 5 11
TICK
CX 0 4 3 7 5 9 8 12 10 14 11 15
TICK
H 3 5 11
TICK
M 4 7 9 12 2 14 1 15
DETECTOR(1, 2, 0) rec[-16] rec[-8]
DETECTOR(2, 1, 0) rec[-15] rec[-7]
DETECTOR(2, 3, 0) rec[-14] rec[-6]
DETECTOR(3, 2, 0) rec[-13] rec[-5]
DETECTOR(1, 0, 0) rec[-12] rec[-4]
DETECTOR(3, 4, 0) rec[-11] rec[-3]
DETECTOR(0, 3, 0) rec[-10] rec[-2]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
M 0 3 6 5 8 11 10 13 16
DETECTOR(1, 0, 0) rec[-13] rec[-8] rec[-7]
DETECTOR(1, 2, 0) rec[-17] rec[-9] rec[-8] rec[-6] rec[-5]
DETECTOR(3, 4, 0) rec[-12] rec[-3] rec[-2]
DETECTOR(3, 2, 0) rec[-14] rec[-5] rec[-4] rec[-2] rec[-1]
OBSERVABLE_INCLUDE(0) rec[-9] rec[-6] rec[-3]"""

    assert str(stim_circuit) == expected


def test_rotated_surface_code_compilation_end_to_end_6():
    """
    Distance: 3
    Noise model: None
    Syndrome extractor: CzExtractor
    Compiler: AncillaPerCheckCompiler
    total_rounds: 3
    Initial States: all Zero
    Final measurements: all Z
    Observables: logical Z
    """
    code = RotatedSurfaceCode(distance=3)
    extractor = CzExtractor(RotatedSurfaceCodeOrderer())
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

    expected = """QUBIT_COORDS(0, 2) 0
QUBIT_COORDS(0, 3) 1
QUBIT_COORDS(1, 0) 2
QUBIT_COORDS(1, 1) 3
QUBIT_COORDS(1, 2) 4
QUBIT_COORDS(1, 3) 5
QUBIT_COORDS(2, 0) 6
QUBIT_COORDS(2, 1) 7
QUBIT_COORDS(2, 2) 8
QUBIT_COORDS(2, 3) 9
QUBIT_COORDS(2, 4) 10
QUBIT_COORDS(3, 1) 11
QUBIT_COORDS(3, 2) 12
QUBIT_COORDS(3, 3) 13
QUBIT_COORDS(3, 4) 14
QUBIT_COORDS(4, 1) 15
QUBIT_COORDS(4, 2) 16
R 0 3 6 5 8 11 10 13 16
TICK
RX 4 7 9 12 2 14 1 15
TICK
H 11 13 5
TICK
CZ 8 4 11 7 13 9 16 12 6 2 5 1
TICK
H 11 13 5
TICK
H 6 8 0
TICK
CZ 5 4 6 7 8 9 13 12 3 2 0 1
TICK
H 6 8 0
TICK
H 8 10 16
TICK
CZ 3 4 8 7 10 9 11 12 13 14 16 15
TICK
H 8 10 16
TICK
H 3 5 11
TICK
CZ 0 4 3 7 5 9 8 12 10 14 11 15
TICK
H 3 5 11
TICK
MX 4 7 9 12 2 14 1 15
DETECTOR(1, 2, 0) rec[-8]
DETECTOR(3, 2, 0) rec[-5]
DETECTOR(1, 0, 0) rec[-4]
DETECTOR(3, 4, 0) rec[-3]
SHIFT_COORDS(0, 0, 1)
TICK
RX 4 7 9 12 2 14 1 15
TICK
H 11 13 5
TICK
CZ 8 4 11 7 13 9 16 12 6 2 5 1
TICK
H 11 13 5
TICK
H 6 8 0
TICK
CZ 5 4 6 7 8 9 13 12 3 2 0 1
TICK
H 6 8 0
TICK
H 8 10 16
TICK
CZ 3 4 8 7 10 9 11 12 13 14 16 15
TICK
H 8 10 16
TICK
H 3 5 11
TICK
CZ 0 4 3 7 5 9 8 12 10 14 11 15
TICK
H 3 5 11
TICK
MX 4 7 9 12 2 14 1 15
DETECTOR(1, 2, 0) rec[-16] rec[-8]
DETECTOR(2, 1, 0) rec[-15] rec[-7]
DETECTOR(2, 3, 0) rec[-14] rec[-6]
DETECTOR(3, 2, 0) rec[-13] rec[-5]
DETECTOR(1, 0, 0) rec[-12] rec[-4]
DETECTOR(3, 4, 0) rec[-11] rec[-3]
DETECTOR(0, 3, 0) rec[-10] rec[-2]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
RX 4 7 9 12 2 14 1 15
TICK
H 11 13 5
TICK
CZ 8 4 11 7 13 9 16 12 6 2 5 1
TICK
H 11 13 5
TICK
H 6 8 0
TICK
CZ 5 4 6 7 8 9 13 12 3 2 0 1
TICK
H 6 8 0
TICK
H 8 10 16
TICK
CZ 3 4 8 7 10 9 11 12 13 14 16 15
TICK
H 8 10 16
TICK
H 3 5 11
TICK
CZ 0 4 3 7 5 9 8 12 10 14 11 15
TICK
H 3 5 11
TICK
MX 4 7 9 12 2 14 1 15
DETECTOR(1, 2, 0) rec[-16] rec[-8]
DETECTOR(2, 1, 0) rec[-15] rec[-7]
DETECTOR(2, 3, 0) rec[-14] rec[-6]
DETECTOR(3, 2, 0) rec[-13] rec[-5]
DETECTOR(1, 0, 0) rec[-12] rec[-4]
DETECTOR(3, 4, 0) rec[-11] rec[-3]
DETECTOR(0, 3, 0) rec[-10] rec[-2]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
M 0 3 6 5 8 11 10 13 16
DETECTOR(1, 0, 0) rec[-13] rec[-8] rec[-7]
DETECTOR(1, 2, 0) rec[-17] rec[-9] rec[-8] rec[-6] rec[-5]
DETECTOR(3, 4, 0) rec[-12] rec[-3] rec[-2]
DETECTOR(3, 2, 0) rec[-14] rec[-5] rec[-4] rec[-2] rec[-1]
OBSERVABLE_INCLUDE(0) rec[-9] rec[-6] rec[-3]"""

    assert str(stim_circuit) == expected

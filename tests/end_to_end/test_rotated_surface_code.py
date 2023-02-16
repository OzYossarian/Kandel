from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models import PhenomenologicalNoise, CircuitLevelNoise
from main.compiling.syndrome_extraction.controlled_gate_orderers.RotatedSurfaceCodeOrderer import (
    RotatedSurfaceCodeOrderer,
)
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CnotExtractor import (
    CnotExtractor,
)
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CzExtractor import (
    CzExtractor,
)
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.pure.CnotCssExtractor import (
    CnotCssExtractor,
)
from main.utils.enums import State


def test_rotated_surface_code_compilation_end_to_end_1():
    """
    Distance: 3
    Noise model: None
    Syndrome extractor: CnotCssExtractor
    Compiler: AncillaPerCheckCompiler
    Layers: 3
    Initial States: all Zero
    Final measurements: all Z
    Observables: logical Z
    """
    code = RotatedSurfaceCode(distance=3)
    extractor = CnotCssExtractor(RotatedSurfaceCodeOrderer())
    compiler = AncillaPerCheckCompiler(syndrome_extractor=extractor)

    data_qubits = code.data_qubits.values()
    initial_states = {qubit: State.Zero for qubit in data_qubits}
    final_measurements = [Pauli(qubit, PauliLetter("Z")) for qubit in data_qubits]
    stim_circuit = compiler.compile_to_stim(
        code=code,
        layers=3,
        initial_states=initial_states,
        final_measurements=final_measurements,
        logical_observables=[code.logical_qubits[0].z],
    )
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
R 0 3 5 6 8 10 11 13 16
TICK
RX 1
R 2 4
RX 7 9
R 12 14
RX 15
TICK
CX 1 5 6 2 8 4 7 11 9 13 16 12
TICK
CX 1 0 3 2 5 4 7 6 9 8 13 12
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
MX 1
M 2 4
MX 7 9
M 12 14
MX 15
DETECTOR(1, 0, 0) rec[-7]
DETECTOR(1, 2, 0) rec[-6]
DETECTOR(3, 2, 0) rec[-3]
DETECTOR(3, 4, 0) rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
RX 1
R 2 4
RX 7 9
R 12 14
RX 15
TICK
CX 1 5 6 2 8 4 7 11 9 13 16 12
TICK
CX 1 0 3 2 5 4 7 6 9 8 13 12
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
MX 1
M 2 4
MX 7 9
M 12 14
MX 15
DETECTOR(1, 0, 0) rec[-15] rec[-7]
DETECTOR(0, 3, 0) rec[-16] rec[-8]
DETECTOR(1, 2, 0) rec[-14] rec[-6]
DETECTOR(2, 1, 0) rec[-13] rec[-5]
DETECTOR(2, 3, 0) rec[-12] rec[-4]
DETECTOR(3, 2, 0) rec[-11] rec[-3]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
DETECTOR(3, 4, 0) rec[-10] rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
RX 1
R 2 4
RX 7 9
R 12 14
RX 15
TICK
CX 1 5 6 2 8 4 7 11 9 13 16 12
TICK
CX 1 0 3 2 5 4 7 6 9 8 13 12
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
MX 1
M 2 4
MX 7 9
M 12 14
MX 15
DETECTOR(1, 0, 0) rec[-15] rec[-7]
DETECTOR(0, 3, 0) rec[-16] rec[-8]
DETECTOR(1, 2, 0) rec[-14] rec[-6]
DETECTOR(2, 1, 0) rec[-13] rec[-5]
DETECTOR(2, 3, 0) rec[-12] rec[-4]
DETECTOR(3, 2, 0) rec[-11] rec[-3]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
DETECTOR(3, 4, 0) rec[-10] rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
M 0 3 5 6 8 10 11 13 16
OBSERVABLE_INCLUDE(0) rec[-9] rec[-7] rec[-4]
DETECTOR(1, 0, 0) rec[-16] rec[-8] rec[-6]
DETECTOR(1, 2, 0) rec[-15] rec[-9] rec[-8] rec[-7] rec[-5]
DETECTOR(3, 2, 0) rec[-12] rec[-5] rec[-3] rec[-2] rec[-1]
DETECTOR(3, 4, 0) rec[-11] rec[-4] rec[-2]"""

    assert str(stim_circuit) == expected


def test_rotated_surface_code_compilation_end_to_end_2():
    """
    Distance: 3
    Noise model: None
    Syndrome extractor: CnotCssExtractor
    Compiler: AncillaPerCheckCompiler
    Layers: 3
    Initial States: all Plus
    Final measurements: all X
    Observables: logical X
    """
    code = RotatedSurfaceCode(distance=3)
    extractor = CnotCssExtractor(RotatedSurfaceCodeOrderer())
    compiler = AncillaPerCheckCompiler(syndrome_extractor=extractor)

    data_qubits = code.data_qubits.values()
    initial_states = {qubit: State.Plus for qubit in data_qubits}
    final_measurements = [Pauli(qubit, PauliLetter("X")) for qubit in data_qubits]
    stim_circuit = compiler.compile_to_stim(
        code=code,
        layers=3,
        initial_states=initial_states,
        final_measurements=final_measurements,
        logical_observables=[code.logical_qubits[0].x],
    )
    print(stim_circuit)
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
RX 0 3 5 6 8 10 11 13 16
TICK
RX 1
R 2 4
RX 7 9
R 12 14
RX 15
TICK
CX 1 5 6 2 8 4 7 11 9 13 16 12
TICK
CX 1 0 3 2 5 4 7 6 9 8 13 12
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
MX 1
M 2 4
MX 7 9
M 12 14
MX 15
DETECTOR(0, 3, 0) rec[-8]
DETECTOR(2, 1, 0) rec[-5]
DETECTOR(2, 3, 0) rec[-4]
DETECTOR(4, 1, 0) rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
RX 1
R 2 4
RX 7 9
R 12 14
RX 15
TICK
CX 1 5 6 2 8 4 7 11 9 13 16 12
TICK
CX 1 0 3 2 5 4 7 6 9 8 13 12
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
MX 1
M 2 4
MX 7 9
M 12 14
MX 15
DETECTOR(1, 0, 0) rec[-15] rec[-7]
DETECTOR(0, 3, 0) rec[-16] rec[-8]
DETECTOR(1, 2, 0) rec[-14] rec[-6]
DETECTOR(2, 1, 0) rec[-13] rec[-5]
DETECTOR(2, 3, 0) rec[-12] rec[-4]
DETECTOR(3, 2, 0) rec[-11] rec[-3]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
DETECTOR(3, 4, 0) rec[-10] rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
RX 1
R 2 4
RX 7 9
R 12 14
RX 15
TICK
CX 1 5 6 2 8 4 7 11 9 13 16 12
TICK
CX 1 0 3 2 5 4 7 6 9 8 13 12
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
MX 1
M 2 4
MX 7 9
M 12 14
MX 15
DETECTOR(1, 0, 0) rec[-15] rec[-7]
DETECTOR(0, 3, 0) rec[-16] rec[-8]
DETECTOR(1, 2, 0) rec[-14] rec[-6]
DETECTOR(2, 1, 0) rec[-13] rec[-5]
DETECTOR(2, 3, 0) rec[-12] rec[-4]
DETECTOR(3, 2, 0) rec[-11] rec[-3]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
DETECTOR(3, 4, 0) rec[-10] rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
MX 0 3 5 6 8 10 11 13 16
OBSERVABLE_INCLUDE(0) rec[-9] rec[-8] rec[-6]
DETECTOR(0, 3, 0) rec[-17] rec[-9] rec[-7]
DETECTOR(2, 1, 0) rec[-14] rec[-8] rec[-6] rec[-5] rec[-3]
DETECTOR(2, 3, 0) rec[-13] rec[-7] rec[-5] rec[-4] rec[-2]
DETECTOR(4, 1, 0) rec[-10] rec[-3] rec[-1]"""

    assert str(stim_circuit) == expected


def test_rotated_surface_code_compilation_end_to_end_3():
    """
    Distance: 3
    Noise model: Phenomenological
    Syndrome extractor: CnotCssExtractor
    Compiler: AncillaPerCheckCompiler
    Layers: 3
    Initial States: all Zero
    Final measurements: all Z
    Observables: logical Z
    """
    code = RotatedSurfaceCode(distance=3)
    extractor = CnotCssExtractor(RotatedSurfaceCodeOrderer())
    compiler = AncillaPerCheckCompiler(
        noise_model=PhenomenologicalNoise(0.1, 0.2), syndrome_extractor=extractor
    )

    data_qubits = code.data_qubits.values()
    initial_states = {qubit: State.Zero for qubit in data_qubits}
    final_measurements = [Pauli(qubit, PauliLetter("Z")) for qubit in data_qubits]
    stim_circuit = compiler.compile_to_stim(
        code=code,
        layers=3,
        initial_states=initial_states,
        final_measurements=final_measurements,
        logical_observables=[code.logical_qubits[0].z],
    )
    print(stim_circuit)
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
R 0 3 5 6 8 10 11 13 16
TICK
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 0 3 5 6 8 10 11 13 16
TICK
RX 1
R 2 4
RX 7 9
R 12 14
RX 15
TICK
CX 1 5 6 2 8 4 7 11 9 13 16 12
TICK
CX 1 0 3 2 5 4 7 6 9 8 13 12
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
MX(0.2) 1
M(0.2) 2 4
MX(0.2) 7 9
M(0.2) 12 14
MX(0.2) 15
DETECTOR(1, 0, 0) rec[-7]
DETECTOR(1, 2, 0) rec[-6]
DETECTOR(3, 2, 0) rec[-3]
DETECTOR(3, 4, 0) rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 0 3 5 6 8 10 11 13 16
TICK
RX 1
R 2 4
RX 7 9
R 12 14
RX 15
TICK
CX 1 5 6 2 8 4 7 11 9 13 16 12
TICK
CX 1 0 3 2 5 4 7 6 9 8 13 12
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
MX(0.2) 1
M(0.2) 2 4
MX(0.2) 7 9
M(0.2) 12 14
MX(0.2) 15
DETECTOR(1, 0, 0) rec[-15] rec[-7]
DETECTOR(0, 3, 0) rec[-16] rec[-8]
DETECTOR(1, 2, 0) rec[-14] rec[-6]
DETECTOR(2, 1, 0) rec[-13] rec[-5]
DETECTOR(2, 3, 0) rec[-12] rec[-4]
DETECTOR(3, 2, 0) rec[-11] rec[-3]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
DETECTOR(3, 4, 0) rec[-10] rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 0 3 5 6 8 10 11 13 16
TICK
RX 1
R 2 4
RX 7 9
R 12 14
RX 15
TICK
CX 1 5 6 2 8 4 7 11 9 13 16 12
TICK
CX 1 0 3 2 5 4 7 6 9 8 13 12
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
MX(0.2) 1
M(0.2) 2 4
MX(0.2) 7 9
M(0.2) 12 14
MX(0.2) 15
DETECTOR(1, 0, 0) rec[-15] rec[-7]
DETECTOR(0, 3, 0) rec[-16] rec[-8]
DETECTOR(1, 2, 0) rec[-14] rec[-6]
DETECTOR(2, 1, 0) rec[-13] rec[-5]
DETECTOR(2, 3, 0) rec[-12] rec[-4]
DETECTOR(3, 2, 0) rec[-11] rec[-3]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
DETECTOR(3, 4, 0) rec[-10] rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
M(0.2) 0 3 5 6 8 10 11 13 16
OBSERVABLE_INCLUDE(0) rec[-9] rec[-7] rec[-4]
DETECTOR(1, 0, 0) rec[-16] rec[-8] rec[-6]
DETECTOR(1, 2, 0) rec[-15] rec[-9] rec[-8] rec[-7] rec[-5]
DETECTOR(3, 2, 0) rec[-12] rec[-5] rec[-3] rec[-2] rec[-1]
DETECTOR(3, 4, 0) rec[-11] rec[-4] rec[-2]"""

    assert str(stim_circuit) == expected


def test_rotated_surface_code_compilation_end_to_end_4():
    """
    Distance: 3
    Noise model: CircuitLevel
    Syndrome extractor: CnotCssExtractor
    Compiler: AncillaPerCheckCompiler
    Layers: 3
    Initial States: all Zero
    Final measurements: all Z
    Observables: logical Z
    """
    code = RotatedSurfaceCode(distance=3)
    extractor = CnotCssExtractor(RotatedSurfaceCodeOrderer())
    compiler = AncillaPerCheckCompiler(
        noise_model=CircuitLevelNoise(0.1, 0.2, 0.3, 0.4, 0.5),
        syndrome_extractor=extractor,
    )

    data_qubits = code.data_qubits.values()
    initial_states = {qubit: State.Zero for qubit in data_qubits}
    final_measurements = [Pauli(qubit, PauliLetter("Z")) for qubit in data_qubits]
    stim_circuit = compiler.compile_to_stim(
        code=code,
        layers=3,
        initial_states=initial_states,
        final_measurements=final_measurements,
        logical_observables=[code.logical_qubits[0].z],
    )
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
R 0 3 5 6 8 10 11 13 16
TICK
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 0 3 5 6 8 10 11 13 16
TICK
RX 1
R 2 4
RX 7 9
R 12 14
RX 15
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 1 2
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 3
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 4
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 5 6
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 7
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 8
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 9
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 10 11
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 12
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 13
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 14 15
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 16
TICK
CX 1 5 6 2 8 4 7 11 9 13 16 12
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 1 5 6 2
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 3
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 8 4 7 11 9 13
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 10
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 16 12
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 14 15
TICK
CX 1 0 3 2 5 4 7 6 9 8 13 12
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 1 0 3 2 5 4 7 6 9 8
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 10 11
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 13 12
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 14 15 16
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 1 2
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 3 4
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 5 6
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 0 4
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 1 2
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 7 3 9 5
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 6
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 8 12 10 14 15 11
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 13 16
TICK
MX(0.5) 1
M(0.5) 2 4
MX(0.5) 7 9
M(0.5) 12 14
MX(0.5) 15
DETECTOR(1, 0, 0) rec[-7]
DETECTOR(1, 2, 0) rec[-6]
DETECTOR(3, 2, 0) rec[-3]
DETECTOR(3, 4, 0) rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 3 5 6 8 10 11 13 16
TICK
RX 1
R 2 4
RX 7 9
R 12 14
RX 15
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 1 2
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 3
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 4
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 5 6
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 7
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 8
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 9
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 10 11
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 12
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 13
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 14 15
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 16
TICK
CX 1 5 6 2 8 4 7 11 9 13 16 12
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 1 5 6 2
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 3
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 8 4 7 11 9 13
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 10
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 16 12
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 14 15
TICK
CX 1 0 3 2 5 4 7 6 9 8 13 12
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 1 0 3 2 5 4 7 6 9 8
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 10 11
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 13 12
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 14 15 16
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 1 2
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 3 4
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 5 6
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 0 4
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 1 2
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 7 3 9 5
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 6
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 8 12 10 14 15 11
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 13 16
TICK
MX(0.5) 1
M(0.5) 2 4
MX(0.5) 7 9
M(0.5) 12 14
MX(0.5) 15
DETECTOR(1, 0, 0) rec[-15] rec[-7]
DETECTOR(0, 3, 0) rec[-16] rec[-8]
DETECTOR(1, 2, 0) rec[-14] rec[-6]
DETECTOR(2, 1, 0) rec[-13] rec[-5]
DETECTOR(2, 3, 0) rec[-12] rec[-4]
DETECTOR(3, 2, 0) rec[-11] rec[-3]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
DETECTOR(3, 4, 0) rec[-10] rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 3 5 6 8 10 11 13 16
TICK
RX 1
R 2 4
RX 7 9
R 12 14
RX 15
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 1 2
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 3
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 4
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 5 6
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 7
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 8
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 9
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 10 11
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 12
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 13
PAULI_CHANNEL_1(0.0333333, 0.0333333, 0.0333333) 14 15
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 16
TICK
CX 1 5 6 2 8 4 7 11 9 13 16 12
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 1 5 6 2
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 3
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 8 4 7 11 9 13
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 10
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 16 12
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 14 15
TICK
CX 1 0 3 2 5 4 7 6 9 8 13 12
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 1 0 3 2 5 4 7 6 9 8
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 10 11
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 13 12
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 14 15 16
TICK
CX 3 4 7 8 9 10 11 12 13 14 15 16
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 1 2
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 3 4
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 5 6
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 7 8 9 10 11 12 13 14 15 16
TICK
CX 0 4 7 3 9 5 8 12 10 14 15 11
TICK
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 0 4
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 1 2
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 7 3 9 5
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 6
PAULI_CHANNEL_2(0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667, 0.0266667) 8 12 10 14 15 11
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 13 16
TICK
MX(0.5) 1
M(0.5) 2 4
MX(0.5) 7 9
M(0.5) 12 14
MX(0.5) 15
DETECTOR(1, 0, 0) rec[-15] rec[-7]
DETECTOR(0, 3, 0) rec[-16] rec[-8]
DETECTOR(1, 2, 0) rec[-14] rec[-6]
DETECTOR(2, 1, 0) rec[-13] rec[-5]
DETECTOR(2, 3, 0) rec[-12] rec[-4]
DETECTOR(3, 2, 0) rec[-11] rec[-3]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
DETECTOR(3, 4, 0) rec[-10] rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.0666667, 0.0666667, 0.0666667) 0 3 5 6 8 10 11 13 16
TICK
M(0.5) 0 3 5 6 8 10 11 13 16
OBSERVABLE_INCLUDE(0) rec[-9] rec[-7] rec[-4]
DETECTOR(1, 0, 0) rec[-16] rec[-8] rec[-6]
DETECTOR(1, 2, 0) rec[-15] rec[-9] rec[-8] rec[-7] rec[-5]
DETECTOR(3, 2, 0) rec[-12] rec[-5] rec[-3] rec[-2] rec[-1]
DETECTOR(3, 4, 0) rec[-11] rec[-4] rec[-2]"""

    assert str(stim_circuit) == expected


def test_rotated_surface_code_compilation_end_to_end_5():
    """
    Distance: 3
    Noise model: None
    Syndrome extractor: CnotExtractor
    Compiler: AncillaPerCheckCompiler
    Layers: 3
    Initial States: all Zero
    Final measurements: all Z
    Observables: logical Z
    """
    code = RotatedSurfaceCode(distance=3)
    extractor = CnotExtractor(RotatedSurfaceCodeOrderer())
    compiler = AncillaPerCheckCompiler(syndrome_extractor=extractor)

    data_qubits = code.data_qubits.values()
    initial_states = {qubit: State.Zero for qubit in data_qubits}
    final_measurements = [Pauli(qubit, PauliLetter("Z")) for qubit in data_qubits]
    stim_circuit = compiler.compile_to_stim(
        code=code,
        layers=3,
        initial_states=initial_states,
        final_measurements=final_measurements,
        logical_observables=[code.logical_qubits[0].z],
    )
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
R 0 3 5 6 8 10 11 13 16
TICK
R 1 2 4 7 9 12 14 15
TICK
H 5 11 13
TICK
CX 5 1 6 2 8 4 11 7 13 9 16 12
TICK
H 5 11 13
TICK
H 0 6 8
TICK
CX 0 1 3 2 5 4 6 7 8 9 13 12
TICK
H 0 6 8
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
M 1 2 4 7 9 12 14 15
DETECTOR(1, 0, 0) rec[-7]
DETECTOR(1, 2, 0) rec[-6]
DETECTOR(3, 2, 0) rec[-3]
DETECTOR(3, 4, 0) rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
R 1 2 4 7 9 12 14 15
TICK
H 5 11 13
TICK
CX 5 1 6 2 8 4 11 7 13 9 16 12
TICK
H 5 11 13
TICK
H 0 6 8
TICK
CX 0 1 3 2 5 4 6 7 8 9 13 12
TICK
H 0 6 8
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
M 1 2 4 7 9 12 14 15
DETECTOR(1, 0, 0) rec[-15] rec[-7]
DETECTOR(0, 3, 0) rec[-16] rec[-8]
DETECTOR(1, 2, 0) rec[-14] rec[-6]
DETECTOR(2, 1, 0) rec[-13] rec[-5]
DETECTOR(2, 3, 0) rec[-12] rec[-4]
DETECTOR(3, 2, 0) rec[-11] rec[-3]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
DETECTOR(3, 4, 0) rec[-10] rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
R 1 2 4 7 9 12 14 15
TICK
H 5 11 13
TICK
CX 5 1 6 2 8 4 11 7 13 9 16 12
TICK
H 5 11 13
TICK
H 0 6 8
TICK
CX 0 1 3 2 5 4 6 7 8 9 13 12
TICK
H 0 6 8
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
M 1 2 4 7 9 12 14 15
DETECTOR(1, 0, 0) rec[-15] rec[-7]
DETECTOR(0, 3, 0) rec[-16] rec[-8]
DETECTOR(1, 2, 0) rec[-14] rec[-6]
DETECTOR(2, 1, 0) rec[-13] rec[-5]
DETECTOR(2, 3, 0) rec[-12] rec[-4]
DETECTOR(3, 2, 0) rec[-11] rec[-3]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
DETECTOR(3, 4, 0) rec[-10] rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
M 0 3 5 6 8 10 11 13 16
OBSERVABLE_INCLUDE(0) rec[-9] rec[-7] rec[-4]
DETECTOR(1, 0, 0) rec[-16] rec[-8] rec[-6]
DETECTOR(1, 2, 0) rec[-15] rec[-9] rec[-8] rec[-7] rec[-5]
DETECTOR(3, 2, 0) rec[-12] rec[-5] rec[-3] rec[-2] rec[-1]
DETECTOR(3, 4, 0) rec[-11] rec[-4] rec[-2]"""

    assert str(stim_circuit) == expected


def test_rotated_surface_code_compilation_end_to_end_6():
    """
    Distance: 3
    Noise model: None
    Syndrome extractor: CzExtractor
    Compiler: AncillaPerCheckCompiler
    Layers: 3
    Initial States: all Zero
    Final measurements: all Z
    Observables: logical Z
    """
    code = RotatedSurfaceCode(distance=3)
    extractor = CzExtractor(RotatedSurfaceCodeOrderer())
    compiler = AncillaPerCheckCompiler(syndrome_extractor=extractor)

    data_qubits = code.data_qubits.values()
    initial_states = {qubit: State.Zero for qubit in data_qubits}
    final_measurements = [Pauli(qubit, PauliLetter("Z")) for qubit in data_qubits]
    stim_circuit = compiler.compile_to_stim(
        code=code,
        layers=3,
        initial_states=initial_states,
        final_measurements=final_measurements,
        logical_observables=[code.logical_qubits[0].z],
    )
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
R 0 3 5 6 8 10 11 13 16
TICK
RX 1 2 4 7 9 12 14 15
TICK
H 5 11 13
TICK
CZ 5 1 6 2 8 4 11 7 13 9 16 12
TICK
H 5 11 13
TICK
H 0 6 8
TICK
CZ 0 1 3 2 5 4 6 7 8 9 13 12
TICK
H 0 6 8
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
MX 1 2 4 7 9 12 14 15
DETECTOR(1, 0, 0) rec[-7]
DETECTOR(1, 2, 0) rec[-6]
DETECTOR(3, 2, 0) rec[-3]
DETECTOR(3, 4, 0) rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
RX 1 2 4 7 9 12 14 15
TICK
H 5 11 13
TICK
CZ 5 1 6 2 8 4 11 7 13 9 16 12
TICK
H 5 11 13
TICK
H 0 6 8
TICK
CZ 0 1 3 2 5 4 6 7 8 9 13 12
TICK
H 0 6 8
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
MX 1 2 4 7 9 12 14 15
DETECTOR(1, 0, 0) rec[-15] rec[-7]
DETECTOR(0, 3, 0) rec[-16] rec[-8]
DETECTOR(1, 2, 0) rec[-14] rec[-6]
DETECTOR(2, 1, 0) rec[-13] rec[-5]
DETECTOR(2, 3, 0) rec[-12] rec[-4]
DETECTOR(3, 2, 0) rec[-11] rec[-3]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
DETECTOR(3, 4, 0) rec[-10] rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
RX 1 2 4 7 9 12 14 15
TICK
H 5 11 13
TICK
CZ 5 1 6 2 8 4 11 7 13 9 16 12
TICK
H 5 11 13
TICK
H 0 6 8
TICK
CZ 0 1 3 2 5 4 6 7 8 9 13 12
TICK
H 0 6 8
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
MX 1 2 4 7 9 12 14 15
DETECTOR(1, 0, 0) rec[-15] rec[-7]
DETECTOR(0, 3, 0) rec[-16] rec[-8]
DETECTOR(1, 2, 0) rec[-14] rec[-6]
DETECTOR(2, 1, 0) rec[-13] rec[-5]
DETECTOR(2, 3, 0) rec[-12] rec[-4]
DETECTOR(3, 2, 0) rec[-11] rec[-3]
DETECTOR(4, 1, 0) rec[-9] rec[-1]
DETECTOR(3, 4, 0) rec[-10] rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
M 0 3 5 6 8 10 11 13 16
OBSERVABLE_INCLUDE(0) rec[-9] rec[-7] rec[-4]
DETECTOR(1, 0, 0) rec[-16] rec[-8] rec[-6]
DETECTOR(1, 2, 0) rec[-15] rec[-9] rec[-8] rec[-7] rec[-5]
DETECTOR(3, 2, 0) rec[-12] rec[-5] rec[-3] rec[-2] rec[-1]
DETECTOR(3, 4, 0) rec[-11] rec[-4] rec[-2]"""

    assert str(stim_circuit) == expected

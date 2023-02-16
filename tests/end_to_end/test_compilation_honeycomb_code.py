from main.codes.tic_tac_toe.HoneycombCode import HoneycombCode
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.NoNoise import NoNoise
from main.compiling.noise.models.CodeCapacityBitFlipNoise import (
    CodeCapacityBitFlipNoise,
)
from main.compiling.noise.models.superconducting_inspired_noise import (
    SuperconductingInspired,
)
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import (
    CxCyCzExtractor,
)
from main.utils.Colour import Blue, Green, Red
from main.utils.enums import State
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
import stim
from main.building_blocks.detectors.Stabilizer import Stabilizer


class HoneycombCodePermuted(TicTacToeCode):
    def __init__(self, distance: int):
        tic_tac_toe = [
            (Blue, PauliLetter("Z")),
            (Red, PauliLetter("X")),
            (Green, PauliLetter("Y")),
        ]

        super().__init__(distance, tic_tac_toe)


def test_e_anyon_memory_experiment_superconducting_noise():
    code = HoneycombCode(4)
    compiler = AncillaPerCheckCompiler(
        noise_model=SuperconductingInspired(0.03), syndrome_extractor=CxCyCzExtractor()
    )
    data_qubits = code.data_qubits.values()
    final_measurements = [Pauli(qubit, PauliLetter("X")) for qubit in data_qubits]
    logical_observables = [code.logical_qubits[0].x, code.logical_qubits[1].x]
    initial_stabilizers = []
    for check in code.check_schedule[0]:
        initial_stabilizers.append(Stabilizer([(0, check)], 0))

    stim_circuit: stim.Circuit = compiler.compile_to_stim(
        code,
        layers=2,
        final_measurements=final_measurements,
        initial_stabilizers=initial_stabilizers,
        logical_observables=logical_observables,
    )
    print(stim_circuit)


# test_e_anyon_memory_experiment_superconducting_noise()


def test_e_anyon_memory_experiment():
    # I don't call this an X or Z memory experiment, because the observables are not X or Z strings.
    # I refer to them by the Z2 anyon that's being pushed around the torus (electric charge here).
    # I don't want to use physics language but this is the best I came up with.
    code = HoneycombCode(4)
    compiler = AncillaPerCheckCompiler(
        noise_model=NoNoise(), syndrome_extractor=CxCyCzExtractor()
    )
    data_qubits = code.data_qubits.values()
    final_measurements = [Pauli(qubit, PauliLetter("X")) for qubit in data_qubits]
    logical_observables = [code.logical_qubits[0].x, code.logical_qubits[1].x]
    initial_stabilizers = []
    for check in code.check_schedule[0]:
        initial_stabilizers.append(Stabilizer([(0, check)], 0))

    stim_circuit: stim.Circuit = compiler.compile_to_stim(
        code,
        layers=2,
        initial_stabilizers=initial_stabilizers,
        final_measurements=final_measurements,
        logical_observables=logical_observables,
    )
    assert (
        str(stim_circuit)
        == """QUBIT_COORDS(0, 2) 0
QUBIT_COORDS(0, 6) 1
QUBIT_COORDS(0, 10) 2
QUBIT_COORDS(1, 1) 3
QUBIT_COORDS(1, 3) 4
QUBIT_COORDS(1, 5) 5
QUBIT_COORDS(1, 7) 6
QUBIT_COORDS(1, 9) 7
QUBIT_COORDS(1, 11) 8
QUBIT_COORDS(2, 0) 9
QUBIT_COORDS(2, 4) 10
QUBIT_COORDS(2, 8) 11
QUBIT_COORDS(4, 0) 12
QUBIT_COORDS(4, 4) 13
QUBIT_COORDS(4, 8) 14
QUBIT_COORDS(6, 0) 15
QUBIT_COORDS(6, 4) 16
QUBIT_COORDS(6, 8) 17
QUBIT_COORDS(7, 1) 18
QUBIT_COORDS(7, 3) 19
QUBIT_COORDS(7, 5) 20
QUBIT_COORDS(7, 7) 21
QUBIT_COORDS(7, 9) 22
QUBIT_COORDS(7, 11) 23
QUBIT_COORDS(8, 2) 24
QUBIT_COORDS(8, 6) 25
QUBIT_COORDS(8, 10) 26
QUBIT_COORDS(10, 2) 27
QUBIT_COORDS(10, 6) 28
QUBIT_COORDS(10, 10) 29
QUBIT_COORDS(12, 2) 30
QUBIT_COORDS(12, 6) 31
QUBIT_COORDS(12, 10) 32
QUBIT_COORDS(13, 1) 33
QUBIT_COORDS(13, 3) 34
QUBIT_COORDS(13, 5) 35
QUBIT_COORDS(13, 7) 36
QUBIT_COORDS(13, 9) 37
QUBIT_COORDS(13, 11) 38
QUBIT_COORDS(14, 0) 39
QUBIT_COORDS(14, 4) 40
QUBIT_COORDS(14, 8) 41
QUBIT_COORDS(16, 0) 42
QUBIT_COORDS(16, 4) 43
QUBIT_COORDS(16, 8) 44
QUBIT_COORDS(18, 0) 45
QUBIT_COORDS(18, 4) 46
QUBIT_COORDS(18, 8) 47
QUBIT_COORDS(19, 1) 48
QUBIT_COORDS(19, 3) 49
QUBIT_COORDS(19, 5) 50
QUBIT_COORDS(19, 7) 51
QUBIT_COORDS(19, 9) 52
QUBIT_COORDS(19, 11) 53
QUBIT_COORDS(20, 2) 54
QUBIT_COORDS(20, 6) 55
QUBIT_COORDS(20, 10) 56
QUBIT_COORDS(22, 2) 57
QUBIT_COORDS(22, 6) 58
QUBIT_COORDS(22, 10) 59
RX 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
TICK
RX 5 8 14 20 23 27 35 38 44 50 53 57
TICK
CX 5 10 8 9 14 11 20 25 23 26 27 24 35 40 38 39 44 41 50 55 53 56 57 54
TICK
CX 57 0 5 1 8 2 14 17 23 15 20 16 27 30 35 31 38 32 44 47 53 45 50 46
TICK
MX 5 8 14 20 23 27 35 38 44 50 53 57
DETECTOR(1, 5) rec[-12]
DETECTOR(1, 11) rec[-11]
DETECTOR(4, 8) rec[-10]
DETECTOR(7, 5) rec[-9]
DETECTOR(10, 2) rec[-7]
DETECTOR(7, 11) rec[-8]
DETECTOR(13, 5) rec[-6]
DETECTOR(13, 11) rec[-5]
DETECTOR(16, 8) rec[-4]
DETECTOR(19, 5) rec[-3]
DETECTOR(22, 2) rec[-1]
DETECTOR(19, 11) rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
RX 4 7 12 19 22 28 34 37 42 49 52 58
TICK
CY 4 10 7 11 12 9 19 24 22 26 28 25 34 40 37 41 42 39 49 54 52 56 58 55
TICK
CY 4 0 58 1 7 2 12 15 19 16 22 17 28 31 34 30 37 32 42 45 49 46 52 47
TICK
MX 4 7 12 19 22 28 34 37 42 49 52 58
OBSERVABLE_INCLUDE(0) rec[-9] rec[-8]
OBSERVABLE_INCLUDE(1) rec[-7] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
RX 3 6 13 18 21 29 33 36 43 48 51 59
TICK
CZ 3 9 6 11 13 10 18 24 21 25 29 26 33 39 36 41 43 40 48 54 51 55 59 56
TICK
CZ 3 0 6 1 59 2 13 16 18 15 21 17 29 32 33 30 36 31 43 46 48 45 51 47
TICK
MX 3 6 13 18 21 29 33 36 43 48 51 59
OBSERVABLE_INCLUDE(0) rec[-9] rec[-8]
OBSERVABLE_INCLUDE(1) rec[-11] rec[-8] rec[-5] rec[-2]
DETECTOR(4, 2, 0) rec[-21] rec[-24] rec[-22] rec[-10] rec[-9] rec[-12]
DETECTOR(10, 8, 0) rec[-17] rec[-20] rec[-19] rec[-8] rec[-7] rec[-5]
DETECTOR(16, 2, 0) rec[-15] rec[-18] rec[-16] rec[-6] rec[-4] rec[-3]
DETECTOR(22, 8, 0) rec[-23] rec[-14] rec[-13] rec[-11] rec[-2] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
RX 5 8 14 20 23 27 35 38 44 50 53 57
TICK
CX 5 10 8 9 14 11 20 25 23 26 27 24 35 40 38 39 44 41 50 55 53 56 57 54
TICK
CX 57 0 5 1 8 2 14 17 23 15 20 16 27 30 35 31 38 32 44 47 53 45 50 46
TICK
MX 5 8 14 20 23 27 35 38 44 50 53 57
OBSERVABLE_INCLUDE(0) rec[-9] rec[-8]
OBSERVABLE_INCLUDE(1) rec[-10] rec[-4]
SHIFT_COORDS(0, 0, 1)
TICK
RX 4 7 12 19 22 28 34 37 42 49 52 58
TICK
CY 4 10 7 11 12 9 19 24 22 26 28 25 34 40 37 41 42 39 49 54 52 56 58 55
TICK
CY 4 0 58 1 7 2 12 15 19 16 22 17 28 31 34 30 37 32 42 45 49 46 52 47
TICK
MX 4 7 12 19 22 28 34 37 42 49 52 58
OBSERVABLE_INCLUDE(0) rec[-9] rec[-8]
OBSERVABLE_INCLUDE(1) rec[-11] rec[-8] rec[-5] rec[-2]
DETECTOR(4, 10, 0) rec[-56] rec[-59] rec[-58] rec[-46] rec[-44] rec[-47] rec[-20] rec[-23] rec[-22] rec[-10] rec[-8] rec[-11]
DETECTOR(10, 4, 0) rec[-54] rec[-57] rec[-55] rec[-45] rec[-43] rec[-42] rec[-18] rec[-21] rec[-19] rec[-9] rec[-7] rec[-6]
DETECTOR(16, 10, 0) rec[-50] rec[-53] rec[-52] rec[-41] rec[-40] rec[-38] rec[-14] rec[-17] rec[-16] rec[-5] rec[-4] rec[-2]
DETECTOR(22, 4, 0) rec[-60] rec[-51] rec[-49] rec[-48] rec[-39] rec[-37] rec[-24] rec[-15] rec[-13] rec[-12] rec[-3] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
RX 3 6 13 18 21 29 33 36 43 48 51 59
TICK
CZ 3 9 6 11 13 10 18 24 21 25 29 26 33 39 36 41 43 40 48 54 51 55 59 56
TICK
CZ 3 0 6 1 59 2 13 16 18 15 21 17 29 32 33 30 36 31 43 46 48 45 51 47
TICK
MX 3 6 13 18 21 29 33 36 43 48 51 59
OBSERVABLE_INCLUDE(0) rec[-9] rec[-8]
OBSERVABLE_INCLUDE(1) rec[-7] rec[-1]
DETECTOR(4, 2, 0) rec[-57] rec[-60] rec[-58] rec[-46] rec[-45] rec[-48] rec[-21] rec[-24] rec[-22] rec[-10] rec[-9] rec[-12]
DETECTOR(10, 8, 0) rec[-53] rec[-56] rec[-55] rec[-44] rec[-43] rec[-41] rec[-17] rec[-20] rec[-19] rec[-8] rec[-7] rec[-5]
DETECTOR(16, 2, 0) rec[-51] rec[-54] rec[-52] rec[-42] rec[-40] rec[-39] rec[-15] rec[-18] rec[-16] rec[-6] rec[-4] rec[-3]
DETECTOR(22, 8, 0) rec[-59] rec[-50] rec[-49] rec[-47] rec[-38] rec[-37] rec[-23] rec[-14] rec[-13] rec[-11] rec[-2] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
MX 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
OBSERVABLE_INCLUDE(0) rec[-18] rec[-16] rec[-15] rec[-14]
OBSERVABLE_INCLUDE(1) rec[-22] rec[-13] rec[-10] rec[-1]
DETECTOR(4, 2, 0) rec[-34] rec[-33] rec[-36] rec[-45] rec[-48] rec[-46] rec[-24] rec[-21] rec[-20] rec[-18] rec[-17] rec[-15]
DETECTOR(4, 6, 0) rec[-32] rec[-35] rec[-34] rec[-58] rec[-57] rec[-60] rec[-68] rec[-71] rec[-70] rec[-23] rec[-20] rec[-19] rec[-17] rec[-16] rec[-14]
DETECTOR(10, 0, 0) rec[-30] rec[-33] rec[-31] rec[-56] rec[-55] rec[-53] rec[-66] rec[-69] rec[-67] rec[-18] rec[-15] rec[-13] rec[-12] rec[-10] rec[-9]
DETECTOR(10, 8, 0) rec[-32] rec[-31] rec[-29] rec[-41] rec[-44] rec[-43] rec[-16] rec[-14] rec[-13] rec[-11] rec[-10] rec[-7]
DETECTOR(16, 2, 0) rec[-30] rec[-28] rec[-27] rec[-39] rec[-42] rec[-40] rec[-12] rec[-9] rec[-8] rec[-6] rec[-5] rec[-3]
DETECTOR(16, 6, 0) rec[-26] rec[-29] rec[-28] rec[-54] rec[-52] rec[-51] rec[-62] rec[-65] rec[-64] rec[-11] rec[-8] rec[-7] rec[-5] rec[-4] rec[-2]
DETECTOR(22, 0, 0) rec[-36] rec[-27] rec[-25] rec[-59] rec[-50] rec[-49] rec[-72] rec[-63] rec[-61] rec[-24] rec[-22] rec[-21] rec[-6] rec[-3] rec[-1]
DETECTOR(22, 8, 0) rec[-35] rec[-26] rec[-25] rec[-47] rec[-38] rec[-37] rec[-23] rec[-22] rec[-19] rec[-4] rec[-2] rec[-1]"""
    )


def test_m_anyon_memory_experiment():
    # I don't call this an X or Z memory experiment, because the observables are not X or Z strings.
    # I refer to them by the Z2 anyon that's being pushed around the torus (magnetic charge here).
    # I don't want to use physics language but this is the best I came up with.
    code = HoneycombCodePermuted(4)
    compiler = AncillaPerCheckCompiler(
        noise_model=CodeCapacityBitFlipNoise(0.1), syndrome_extractor=CxCyCzExtractor()
    )
    data_qubits = code.data_qubits.values()
    initial_stabilizers = []
    for check in code.check_schedule[0]:
        initial_stabilizers.append(Stabilizer([(0, check)], 0))
    final_measurements = [Pauli(qubit, PauliLetter("Z")) for qubit in data_qubits]
    logical_observables = [code.logical_qubits[0].z, code.logical_qubits[1].z]
    stim_circuit: stim.Circuit = compiler.compile_to_stim(
        code,
        layers=2,
        initial_stabilizers=initial_stabilizers,
        final_measurements=final_measurements,
        logical_observables=logical_observables,
    )

    expected = stim.Circuit(
        """
        QUBIT_COORDS(0, 2) 0
QUBIT_COORDS(0, 6) 1
QUBIT_COORDS(0, 10) 2
QUBIT_COORDS(1, 1) 3
QUBIT_COORDS(1, 3) 4
QUBIT_COORDS(1, 5) 5
QUBIT_COORDS(1, 7) 6
QUBIT_COORDS(1, 9) 7
QUBIT_COORDS(1, 11) 8
QUBIT_COORDS(2, 0) 9
QUBIT_COORDS(2, 4) 10
QUBIT_COORDS(2, 8) 11
QUBIT_COORDS(4, 0) 12
QUBIT_COORDS(4, 4) 13
QUBIT_COORDS(4, 8) 14
QUBIT_COORDS(6, 0) 15
QUBIT_COORDS(6, 4) 16
QUBIT_COORDS(6, 8) 17
QUBIT_COORDS(7, 1) 18
QUBIT_COORDS(7, 3) 19
QUBIT_COORDS(7, 5) 20
QUBIT_COORDS(7, 7) 21
QUBIT_COORDS(7, 9) 22
QUBIT_COORDS(7, 11) 23
QUBIT_COORDS(8, 2) 24
QUBIT_COORDS(8, 6) 25
QUBIT_COORDS(8, 10) 26
QUBIT_COORDS(10, 2) 27
QUBIT_COORDS(10, 6) 28
QUBIT_COORDS(10, 10) 29
QUBIT_COORDS(12, 2) 30
QUBIT_COORDS(12, 6) 31
QUBIT_COORDS(12, 10) 32
QUBIT_COORDS(13, 1) 33
QUBIT_COORDS(13, 3) 34
QUBIT_COORDS(13, 5) 35
QUBIT_COORDS(13, 7) 36
QUBIT_COORDS(13, 9) 37
QUBIT_COORDS(13, 11) 38
QUBIT_COORDS(14, 0) 39
QUBIT_COORDS(14, 4) 40
QUBIT_COORDS(14, 8) 41
QUBIT_COORDS(16, 0) 42
QUBIT_COORDS(16, 4) 43
QUBIT_COORDS(16, 8) 44
QUBIT_COORDS(18, 0) 45
QUBIT_COORDS(18, 4) 46
QUBIT_COORDS(18, 8) 47
QUBIT_COORDS(19, 1) 48
QUBIT_COORDS(19, 3) 49
QUBIT_COORDS(19, 5) 50
QUBIT_COORDS(19, 7) 51
QUBIT_COORDS(19, 9) 52
QUBIT_COORDS(19, 11) 53
QUBIT_COORDS(20, 2) 54
QUBIT_COORDS(20, 6) 55
QUBIT_COORDS(20, 10) 56
QUBIT_COORDS(22, 2) 57
QUBIT_COORDS(22, 6) 58
QUBIT_COORDS(22, 10) 59
R 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
TICK
PAULI_CHANNEL_1(0.1, 0, 0) 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
TICK
RX 3 6 13 18 21 29 33 36 43 48 51 59
TICK
CZ 3 9 6 11 13 10 18 24 21 25 29 26 33 39 36 41 43 40 48 54 51 55 59 56
TICK
CZ 3 0 6 1 59 2 13 16 18 15 21 17 29 32 33 30 36 31 43 46 48 45 51 47
TICK
MX 3 6 13 18 21 29 33 36 43 48 51 59
DETECTOR(1, 1) rec[-12]
DETECTOR(1, 7) rec[-11]
DETECTOR(4, 4) rec[-10]
DETECTOR(7, 1) rec[-9]
DETECTOR(7, 7) rec[-8]
DETECTOR(13, 1) rec[-6]
DETECTOR(10, 10) rec[-7]
DETECTOR(13, 7) rec[-5]
DETECTOR(16, 4) rec[-4]
DETECTOR(19, 1) rec[-3]
DETECTOR(19, 7) rec[-2]
DETECTOR(22, 10) rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.1, 0, 0) 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
TICK
RX 5 8 14 20 23 27 35 38 44 50 53 57
TICK
CX 5 10 8 9 14 11 20 25 23 26 27 24 35 40 38 39 44 41 50 55 53 56 57 54
TICK
CX 57 0 5 1 8 2 14 17 23 15 20 16 27 30 35 31 38 32 44 47 53 45 50 46
TICK
MX 5 8 14 20 23 27 35 38 44 50 53 57
OBSERVABLE_INCLUDE(0) rec[-9] rec[-8]
OBSERVABLE_INCLUDE(1) rec[-7] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.1, 0, 0) 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
TICK
RX 4 7 12 19 22 28 34 37 42 49 52 58
TICK
CY 4 10 7 11 12 9 19 24 22 26 28 25 34 40 37 41 42 39 49 54 52 56 58 55
TICK
CY 4 0 58 1 7 2 12 15 19 16 22 17 28 31 34 30 37 32 42 45 49 46 52 47
TICK
MX 4 7 12 19 22 28 34 37 42 49 52 58
OBSERVABLE_INCLUDE(0) rec[-9] rec[-8]
OBSERVABLE_INCLUDE(1) rec[-12] rec[-9] rec[-6] rec[-3]
DETECTOR(4, 10, 0) rec[-20] rec[-23] rec[-22] rec[-10] rec[-8] rec[-11]
DETECTOR(10, 4, 0) rec[-18] rec[-21] rec[-19] rec[-9] rec[-7] rec[-6]
DETECTOR(16, 10, 0) rec[-14] rec[-17] rec[-16] rec[-5] rec[-4] rec[-2]
DETECTOR(22, 4, 0) rec[-24] rec[-15] rec[-13] rec[-12] rec[-3] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.1, 0, 0) 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
TICK
RX 3 6 13 18 21 29 33 36 43 48 51 59
TICK
CZ 3 9 6 11 13 10 18 24 21 25 29 26 33 39 36 41 43 40 48 54 51 55 59 56
TICK
CZ 3 0 6 1 59 2 13 16 18 15 21 17 29 32 33 30 36 31 43 46 48 45 51 47
TICK
MX 3 6 13 18 21 29 33 36 43 48 51 59
OBSERVABLE_INCLUDE(0) rec[-9] rec[-8]
OBSERVABLE_INCLUDE(1) rec[-10] rec[-4]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.1, 0, 0) 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
TICK
RX 5 8 14 20 23 27 35 38 44 50 53 57
TICK
CX 5 10 8 9 14 11 20 25 23 26 27 24 35 40 38 39 44 41 50 55 53 56 57 54
TICK
CX 57 0 5 1 8 2 14 17 23 15 20 16 27 30 35 31 38 32 44 47 53 45 50 46
TICK
MX 5 8 14 20 23 27 35 38 44 50 53 57
OBSERVABLE_INCLUDE(0) rec[-9] rec[-8]
OBSERVABLE_INCLUDE(1) rec[-12] rec[-9] rec[-6] rec[-3]
DETECTOR(4, 6, 0) rec[-56] rec[-59] rec[-58] rec[-46] rec[-45] rec[-48] rec[-20] rec[-23] rec[-22] rec[-10] rec[-9] rec[-12]
DETECTOR(10, 0, 0) rec[-54] rec[-57] rec[-55] rec[-44] rec[-43] rec[-41] rec[-18] rec[-21] rec[-19] rec[-8] rec[-7] rec[-5]
DETECTOR(16, 6, 0) rec[-50] rec[-53] rec[-52] rec[-42] rec[-40] rec[-39] rec[-14] rec[-17] rec[-16] rec[-6] rec[-4] rec[-3]
DETECTOR(22, 0, 0) rec[-60] rec[-51] rec[-49] rec[-47] rec[-38] rec[-37] rec[-24] rec[-15] rec[-13] rec[-11] rec[-2] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.1, 0, 0) 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
TICK
RX 4 7 12 19 22 28 34 37 42 49 52 58
TICK
CY 4 10 7 11 12 9 19 24 22 26 28 25 34 40 37 41 42 39 49 54 52 56 58 55
TICK
CY 4 0 58 1 7 2 12 15 19 16 22 17 28 31 34 30 37 32 42 45 49 46 52 47
TICK
MX 4 7 12 19 22 28 34 37 42 49 52 58
OBSERVABLE_INCLUDE(0) rec[-9] rec[-8]
OBSERVABLE_INCLUDE(1) rec[-7] rec[-1]
DETECTOR(4, 10, 0) rec[-56] rec[-59] rec[-58] rec[-46] rec[-44] rec[-47] rec[-20] rec[-23] rec[-22] rec[-10] rec[-8] rec[-11]
DETECTOR(10, 4, 0) rec[-54] rec[-57] rec[-55] rec[-45] rec[-43] rec[-42] rec[-18] rec[-21] rec[-19] rec[-9] rec[-7] rec[-6]
DETECTOR(16, 10, 0) rec[-50] rec[-53] rec[-52] rec[-41] rec[-40] rec[-38] rec[-14] rec[-17] rec[-16] rec[-5] rec[-4] rec[-2]
DETECTOR(22, 4, 0) rec[-60] rec[-51] rec[-49] rec[-48] rec[-39] rec[-37] rec[-24] rec[-15] rec[-13] rec[-12] rec[-3] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
M 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
OBSERVABLE_INCLUDE(0) rec[-17] rec[-16] rec[-15] rec[-13]
OBSERVABLE_INCLUDE(1) rec[-23] rec[-14] rec[-11] rec[-2]
DETECTOR(4, 2, 0) rec[-33] rec[-36] rec[-34] rec[-58] rec[-57] rec[-60] rec[-69] rec[-72] rec[-70] rec[-24] rec[-21] rec[-20] rec[-18] rec[-17] rec[-15]
DETECTOR(4, 10, 0) rec[-34] rec[-32] rec[-35] rec[-44] rec[-47] rec[-46] rec[-22] rec[-21] rec[-19] rec[-18] rec[-16] rec[-13]
DETECTOR(10, 4, 0) rec[-33] rec[-31] rec[-30] rec[-42] rec[-45] rec[-43] rec[-17] rec[-15] rec[-14] rec[-12] rec[-11] rec[-8]
DETECTOR(10, 8, 0) rec[-29] rec[-32] rec[-31] rec[-56] rec[-55] rec[-53] rec[-65] rec[-68] rec[-67] rec[-16] rec[-14] rec[-13] rec[-11] rec[-10] rec[-7]
DETECTOR(16, 2, 0) rec[-27] rec[-30] rec[-28] rec[-54] rec[-52] rec[-51] rec[-63] rec[-66] rec[-64] rec[-12] rec[-9] rec[-8] rec[-6] rec[-5] rec[-3]
DETECTOR(22, 4, 0) rec[-36] rec[-27] rec[-25] rec[-48] rec[-39] rec[-37] rec[-24] rec[-23] rec[-20] rec[-5] rec[-3] rec[-2]
DETECTOR(16, 10, 0) rec[-29] rec[-28] rec[-26] rec[-38] rec[-41] rec[-40] rec[-10] rec[-9] rec[-7] rec[-6] rec[-4] rec[-1]
DETECTOR(22, 8, 0) rec[-35] rec[-26] rec[-25] rec[-59] rec[-50] rec[-49] rec[-71] rec[-62] rec[-61] rec[-23] rec[-22] rec[-19] rec[-4] rec[-2] rec[-1]
        """
    )

    assert stim_circuit == expected


test_m_anyon_memory_experiment()
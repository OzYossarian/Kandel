from main.codes.tic_tac_toe.gauge_honeycomb_code import GaugeHoneycombCode
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.CodeCapacityBitFlipNoise import CodeCapacityBitFlipNoise
from main.compiling.noise.models.CircuitLevelNoise import CircuitLevelNoise
from main.compiling.noise.models.NoNoise import NoNoise
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CnotExtractor import CnotExtractor
from main.utils.Colour import Blue, Green, Red
from main.utils.enums import State
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
import stim
import stimcirq


def test_e_anyon_memory_experiment():
    # I don't call this an X or Z memory experiment, because the observables are not X or Z strings.
    # I refer to them by the Z2 anyon that's being pushed around the torus (electric charge here).
    # I don't want to use physics language but this is the best I came up with.
    code = GaugeHoneycombCode(4)
    """
    for detector in code.detector_schedule[4]:
        for check in detector.timed_checks:
            assert check[0] == 0 or check[0] == -2

    for detector in code.detector_schedule[4]:
        for check in detector.lid:
            print(check[0],'0')
            assert check[0] == 0 or check[0] == -2
    """

    compiler = AncillaPerCheckCompiler(noise_model=CodeCapacityBitFlipNoise(0.1), syndrome_extractor=CxCyCzExtractor())
#    compiler = AncillaPerCheckCompiler(noise_model=NoNoise(), syndrome_extractor=CxCyCzExtractor())
#    compiler = AncillaPerCheckCompiler(noise_model=CircuitLevelNoise(0.1,0.1,0.1,0.1,0.1), syndrome_extractor=CxCyCzExtractor())
    data_qubits = code.data_qubits.values()
    data_qubit_initial_states = {qubit: State.Plus for qubit in data_qubits}
    final_measurements = [Pauli(qubit, PauliLetter('X')) for qubit in data_qubits]
    logical_observables = [code.logical_qubits[0].x]#, code.logical_qubits[1].x]
    stim_circuit: stim.Circuit = compiler.compile_to_stim(code,layers=2, 
                                                          initial_states= data_qubit_initial_states, 
                                                          final_measurements=final_measurements,
                                                          logical_observables=logical_observables)
    print(stim_circuit.num_detectors)
    assert stim_circuit.num_detectors == 196
    print(stim_circuit)
    print(stimcirq.stim_circuit_to_cirq_circuit(stim_circuit), file=open('stimcirq.txt','w'))
    print(stim_circuit.detector_error_model(approximate_disjoint_errors=True, decompose_errors=False),file=open('dem.txt','w'))
#    explained_errors = stim_circuit.explain_detector_error_model_errors(dem_filter=stim.DetectorErrorModel('error(0.02613805827160493866) D76 D104 D120 L0'), 
#                                                                        reduce_to_one_representative_error=True)
#    print(explained_errors[0])
#    print(stim_circuit, file=open('circ.txt','w'))

    #    print(tim_circuit.detector_error_model(approximate_disjoint_errors=True)
    stim_circuit.detector_error_model(approximate_disjoint_errors=True,decompose_errors=True).diagram(type="match-graph-3d")
test_e_anyon_memory_experiment()


def test_m_anyon_memory_experiment():
    # I don't call this an X or Z memory experiment, because the observables are not X or Z strings.
    # I refer to them by the Z2 anyon that's being pushed around the torus (magnetic charge here).
    # I don't want to use physics language but this is the best I came up with.
    #    code = HoneycombCodePermuted(4)
    compiler = AncillaPerCheckCompiler(noise_model=CodeCapacityBitFlipNoise(0.1), syndrome_extractor=CxCyCzExtractor())
    data_qubits = code.data_qubits.values()
    data_qubit_initial_states = {qubit: State.Zero for qubit in data_qubits}
    final_measurements = [Pauli(qubit, PauliLetter('Z')) for qubit in data_qubits]
    logical_observables = [code.logical_qubits[0].z,code.logical_qubits[1].z ]
    stim_circuit: stim.Circuit = compiler.compile_to_stim(code,layers=2, 
                                                          initial_states= data_qubit_initial_states, 
                                                          final_measurements=final_measurements,
                                                          logical_observables=logical_observables)

    
    expected = stim.Circuit("""QUBIT_COORDS(0, 2) 0
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
RX 21 6 13 33 18 29 51 36 43 3 48 59
TICK
CZ 21 25 6 11 13 10 33 39 18 24 29 26 51 55 36 41 43 40 3 9 48 54 59 56
TICK
CZ 21 17 6 1 13 16 33 30 18 15 29 32 51 47 36 31 43 46 3 0 48 45 59 2
TICK
MX 21 6 13 33 18 29 51 36 43 3 48 59
DETECTOR(10, 8, 0) rec[-12] rec[-7] rec[-5]
DETECTOR(4, 2, 0) rec[-10] rec[-8] rec[-3]
DETECTOR(16, 2, 0) rec[-9] rec[-4] rec[-2]
DETECTOR(22, 8, 0) rec[-11] rec[-6] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.1, 0, 0) 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
TICK
RX 23 8 14 35 20 27 53 38 44 5 50 57
TICK
CX 23 26 8 9 14 11 35 40 20 25 27 24 53 56 38 39 44 41 5 10 50 55 57 54
TICK
CX 23 15 8 2 14 17 35 31 20 16 27 30 53 45 38 32 44 47 5 1 50 46 57 0
TICK
MX 23 8 14 35 20 27 53 38 44 5 50 57
OBSERVABLE_INCLUDE(0) rec[-12] rec[-8]
OBSERVABLE_INCLUDE(1) rec[-7] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.1, 0, 0) 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
TICK
RX 19 4 12 37 22 28 49 34 42 7 52 58
TICK
CY 19 24 4 10 12 9 37 41 22 26 28 25 49 54 34 40 42 39 7 11 52 56 58 55
TICK
CY 19 16 4 0 12 15 37 32 22 17 28 31 49 46 34 30 42 45 7 2 52 47 58 1
TICK
MX 19 4 12 37 22 28 49 34 42 7 52 58
DETECTOR(10, 4, 0) rec[-21] rec[-20] rec[-19] rec[-12] rec[-7] rec[-5]
DETECTOR(4, 10, 0) rec[-24] rec[-23] rec[-22] rec[-10] rec[-8] rec[-3]
DETECTOR(16, 10, 0) rec[-18] rec[-17] rec[-16] rec[-9] rec[-4] rec[-2]
DETECTOR(22, 4, 0) rec[-15] rec[-14] rec[-13] rec[-11] rec[-6] rec[-1]
OBSERVABLE_INCLUDE(0) rec[-12] rec[-8]
OBSERVABLE_INCLUDE(1) rec[-12] rec[-11] rec[-6] rec[-5]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.1, 0, 0) 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
TICK
RX 21 6 13 33 18 29 51 36 43 3 48 59
TICK
CZ 21 25 6 11 13 10 33 39 18 24 29 26 51 55 36 41 43 40 3 9 48 54 59 56
TICK
CZ 21 17 6 1 13 16 33 30 18 15 29 32 51 47 36 31 43 46 3 0 48 45 59 2
TICK
MX 21 6 13 33 18 29 51 36 43 3 48 59
OBSERVABLE_INCLUDE(0) rec[-12] rec[-8]
OBSERVABLE_INCLUDE(1) rec[-10] rec[-4]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.1, 0, 0) 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
TICK
RX 23 8 14 35 20 27 53 38 44 5 50 57
TICK
CX 23 26 8 9 14 11 35 40 20 25 27 24 53 56 38 39 44 41 5 10 50 55 57 54
TICK
CX 23 15 8 2 14 17 35 31 20 16 27 30 53 45 38 32 44 47 5 1 50 46 57 0
TICK
MX 23 8 14 35 20 27 53 38 44 5 50 57
DETECTOR(10, 0, 0) rec[-57] rec[-56] rec[-55] rec[-48] rec[-43] rec[-41] rec[-21] rec[-20] rec[-19] rec[-12] rec[-7] rec[-5]
DETECTOR(4, 6, 0) rec[-60] rec[-59] rec[-58] rec[-46] rec[-44] rec[-39] rec[-24] rec[-23] rec[-22] rec[-10] rec[-8] rec[-3]
DETECTOR(16, 6, 0) rec[-54] rec[-53] rec[-52] rec[-45] rec[-40] rec[-38] rec[-18] rec[-17] rec[-16] rec[-9] rec[-4] rec[-2]
DETECTOR(22, 0, 0) rec[-51] rec[-50] rec[-49] rec[-47] rec[-42] rec[-37] rec[-15] rec[-14] rec[-13] rec[-11] rec[-6] rec[-1]
OBSERVABLE_INCLUDE(0) rec[-12] rec[-8]
OBSERVABLE_INCLUDE(1) rec[-9] rec[-8] rec[-3] rec[-2]
SHIFT_COORDS(0, 0, 1)
TICK
PAULI_CHANNEL_1(0.1, 0, 0) 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
TICK
RX 19 4 12 37 22 28 49 34 42 7 52 58
TICK
CY 19 24 4 10 12 9 37 41 22 26 28 25 49 54 34 40 42 39 7 11 52 56 58 55
TICK
CY 19 16 4 0 12 15 37 32 22 17 28 31 49 46 34 30 42 45 7 2 52 47 58 1
TICK
MX 19 4 12 37 22 28 49 34 42 7 52 58
DETECTOR(10, 4, 0) rec[-57] rec[-56] rec[-55] rec[-48] rec[-43] rec[-41] rec[-21] rec[-20] rec[-19] rec[-12] rec[-7] rec[-5]
DETECTOR(4, 10, 0) rec[-60] rec[-59] rec[-58] rec[-46] rec[-44] rec[-39] rec[-24] rec[-23] rec[-22] rec[-10] rec[-8] rec[-3]
DETECTOR(16, 10, 0) rec[-54] rec[-53] rec[-52] rec[-45] rec[-40] rec[-38] rec[-18] rec[-17] rec[-16] rec[-9] rec[-4] rec[-2]
DETECTOR(22, 4, 0) rec[-51] rec[-50] rec[-49] rec[-47] rec[-42] rec[-37] rec[-15] rec[-14] rec[-13] rec[-11] rec[-6] rec[-1]
OBSERVABLE_INCLUDE(0) rec[-12] rec[-8]
OBSERVABLE_INCLUDE(1) rec[-7] rec[-1]
SHIFT_COORDS(0, 0, 1)
TICK
M 0 1 2 9 10 11 15 16 17 24 25 26 30 31 32 39 40 41 45 46 47 54 55 56
DETECTOR(4, 2, 0) rec[-36] rec[-35] rec[-34] rec[-58] rec[-56] rec[-51] rec[-72] rec[-71] rec[-70] rec[-24] rec[-21] rec[-20] rec[-18] rec[-17] rec[-15]
DETECTOR(4, 10, 0) rec[-34] rec[-32] rec[-27] rec[-48] rec[-47] rec[-46] rec[-22] rec[-21] rec[-19] rec[-18] rec[-16] rec[-13]
DETECTOR(10, 4, 0) rec[-36] rec[-31] rec[-29] rec[-45] rec[-44] rec[-43] rec[-17] rec[-15] rec[-14] rec[-12] rec[-11] rec[-8]
DETECTOR(10, 8, 0) rec[-33] rec[-32] rec[-31] rec[-60] rec[-55] rec[-53] rec[-69] rec[-68] rec[-67] rec[-16] rec[-14] rec[-13] rec[-11] rec[-10] rec[-7]
DETECTOR(16, 2, 0) rec[-30] rec[-29] rec[-28] rec[-57] rec[-52] rec[-50] rec[-66] rec[-65] rec[-64] rec[-12] rec[-9] rec[-8] rec[-6] rec[-5] rec[-3]
DETECTOR(22, 4, 0) rec[-35] rec[-30] rec[-25] rec[-39] rec[-38] rec[-37] rec[-24] rec[-23] rec[-20] rec[-5] rec[-3] rec[-2]
DETECTOR(16, 10, 0) rec[-33] rec[-28] rec[-26] rec[-42] rec[-41] rec[-40] rec[-10] rec[-9] rec[-7] rec[-6] rec[-4] rec[-1]
DETECTOR(22, 8, 0) rec[-27] rec[-26] rec[-25] rec[-59] rec[-54] rec[-49] rec[-63] rec[-62] rec[-61] rec[-23] rec[-22] rec[-19] rec[-4] rec[-2] rec[-1]
OBSERVABLE_INCLUDE(1) rec[-23] rec[-14] rec[-11] rec[-2]
OBSERVABLE_INCLUDE(0) rec[-17] rec[-16] rec[-15] rec[-13]""")

    assert stim_circuit == expected
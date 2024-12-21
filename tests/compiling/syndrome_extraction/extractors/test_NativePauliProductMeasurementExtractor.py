from unittest.mock import Mock
from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.Circuit import Circuit
from main.compiling.noise.models import EM3, NoNoise, NoiseModel
from main.compiling.noise.noises import OneBitNoise, TwoQubitNoise
from main.compiling.syndrome_extraction.extractors.NativePauliProductMeasurementsExtractor import NativePauliProductMeasurementsExtractor

# write a function that generates the circuit


def gen_rep_code_circ(noise_model: NoiseModel):
    extractor = NativePauliProductMeasurementsExtractor(parallelize=True)
    circuit = Circuit()
    compiler = Mock()
    compiler.noise_model = noise_model
    compiler.noise_model.multi_qubit_measurement = (None, None)
    qubits = [Qubit(j) for j in range(4)]

    tick = 0
    checks = [
        Check([Pauli(qubits[0], PauliLetter('X')),
              Pauli(qubits[1], PauliLetter('X'))]),
        Check([Pauli(qubits[2], PauliLetter('Z')), Pauli(qubits[3], PauliLetter('Z'))])]
    tick = extractor.extract_checks(checks, 0, tick, circuit, compiler)

    checks = [Check([
        Pauli(qubits[0], PauliLetter('X', -1)),
        Pauli(qubits[1], PauliLetter('Y')),
        Pauli(qubits[2], PauliLetter('Z')),
        Pauli(qubits[3], PauliLetter('I'))])]
    tick = extractor.extract_checks(checks, 1, tick, circuit, compiler)

    stim_circuit = circuit.to_stim(
        None, resonator_idling_noise=None, track_coords=False, track_progress=False)
    return (str(stim_circuit))


def test_native_mpp_extractor_end_to_end_noiseless():
    expected = "MPP X0*X1 Z2*Z3\nTICK\nMPP !X0*Y1*Z2"
    assert gen_rep_code_circ(NoNoise) == expected


def test_native_mpp_extractor_end_to_end_EM3():
    # the noise before the MPPs has not been added yet, this is done by the compiler
    expected = """PAULI_CHANNEL_2(0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667) 0 1 2 3
TICK
MPP(0.1) X0*X1 Z2*Z3
TICK
PAULI_CHANNEL_2(0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667, 0.00666667) 0 1 2 3
TICK
MPP(0.1) !X0*Y1*Z2"""

    assert gen_rep_code_circ(EM3(0.1)) == expected



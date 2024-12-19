from unittest.mock import Mock
from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.Circuit import Circuit
from main.compiling.syndrome_extraction.extractors.NativePauliProductMeasurementsExtractor import NativePauliProductMeasurementsExtractor


def test_native_mpp_extractor_end_to_end():
    extractor = NativePauliProductMeasurementsExtractor(parallelize=True)
    circuit = Circuit()
    compiler = Mock()
    compiler.noise_model = Mock()
    compiler.noise_model.measurement = None
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
    result = str(stim_circuit)
    expected = "MPP X0*X1 Z2*Z3\nTICK\nMPP !X0*Y1*Z2"
    assert result == expected

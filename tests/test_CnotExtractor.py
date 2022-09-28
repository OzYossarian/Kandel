from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.Circuit import Circuit
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CnotExtractor import CnotExtractor
from main.enums import State
from tests.utils.checks import create_check
from tests.utils.instructions import MockInstruction


def test_cnot_extractor_on_XYZ_check():
    # Not a unit test, but more of an end-to-end test - check that this
    # extractor builds the expected syndrome extraction circuit for an XYZ
    # check.
    check = create_check(['X', 'Y', 'Z'])
    data_qubits = [pauli.qubit for pauli in check.paulis.values()]
    ancilla = Qubit(-1)
    check.ancilla = ancilla

    initialisation_instructions = {State.Zero: ['RZ']}
    measurement_instructions = {PauliLetter('Z'): ['MZ']}
    extractor = CnotExtractor(
        initialisation_instructions=initialisation_instructions,
        measurement_instructions=measurement_instructions)
    compiler = AncillaPerCheckCompiler()
    circuit = Circuit()

    extractor.extract_checks([check], 0, 0, circuit, compiler)

    # In `expected` we use MockInstructions rather than Instructions -
    # equality comparison between Instructions is instance-based, rather
    # than data-based, for reasons explained in the MockInstruction class.
    expected = {
        # Initialise ancilla
        0: {
            ancilla: [MockInstruction([ancilla], 'RZ')]},
        # Extract X check
        2: {
            data_qubits[0]: [MockInstruction([data_qubits[0]], 'H')]},
        4: {
            data_qubits[0]: [MockInstruction([data_qubits[0], ancilla], 'CNOT')],
            ancilla: [MockInstruction([data_qubits[0], ancilla], 'CNOT')]},
        6: {
            data_qubits[0]: [MockInstruction([data_qubits[0]], 'H')]},
        # Extract Y check
        8: {
            data_qubits[1]: [MockInstruction([data_qubits[1]], 'H_YZ')]},
        10: {
            data_qubits[1]: [MockInstruction([data_qubits[1], ancilla], 'CNOT')],
            ancilla: [MockInstruction([data_qubits[1], ancilla], 'CNOT')]},
        12: {
            data_qubits[1]: [MockInstruction([data_qubits[1]], 'H_YZ')]},
        # Extract Z check
        14: {
            data_qubits[2]: [MockInstruction([data_qubits[2], ancilla], 'CNOT')],
            ancilla: [MockInstruction([data_qubits[2], ancilla], 'CNOT')]},
        # Measure ancilla
        16: {
            ancilla: [MockInstruction([ancilla], 'MZ', is_measurement=True)]}
    }
    assert circuit.instructions == expected

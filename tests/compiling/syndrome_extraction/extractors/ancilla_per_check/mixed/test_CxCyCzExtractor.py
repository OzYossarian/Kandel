from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.Circuit import Circuit
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
from main.utils.enums import State
from tests.building_blocks.utils_checks import specific_check
from tests.compiling.utils_instructions import MockInstruction


def test_cx_cy_cz_extractor_on_XYZ_check():
    # Not a unit test, but more of an end-to-end test - check that this
    # extractor builds the expected syndrome extraction circuit for an XYZ
    # check.
    check = specific_check(['X', 'Y', 'Z'])
    data_qubits = [pauli.qubit for pauli in check.paulis.values()]
    ancilla = Qubit(-1)
    check.ancilla = ancilla

    initialisation_instructions = {State.Plus: ['RX']}
    measurement_instructions = {PauliLetter('X'): ['MX']}
    extractor = CxCyCzExtractor(
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
            ancilla: [MockInstruction([ancilla], 'RX')]},
        # Extract X check
        2: {
            data_qubits[0]: [MockInstruction([ancilla, data_qubits[0]], 'CX')],
            ancilla: [MockInstruction([ancilla, data_qubits[0]], 'CX')]},
        # Extract Y check
        4: {
            data_qubits[1]: [MockInstruction([ancilla, data_qubits[1]], 'CY')],
            ancilla: [MockInstruction([ancilla, data_qubits[1]], 'CY')]},
        # Extract Z check
        6: {
            data_qubits[2]: [MockInstruction([ancilla, data_qubits[2]], 'CZ')],
            ancilla: [MockInstruction([ancilla, data_qubits[2]], 'CZ')]},
        # Measure ancilla
        8: {
            ancilla: [MockInstruction([ancilla], 'MX', is_measurement=True)]}
    }
    assert circuit.instructions == expected


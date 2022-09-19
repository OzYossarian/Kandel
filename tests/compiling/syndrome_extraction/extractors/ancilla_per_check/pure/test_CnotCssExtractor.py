from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.Circuit import Circuit
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.pure.CnotCssExtractor import CnotCssExtractor
from main.utils.enums import State
from tests.building_blocks.utils_checks import specific_check
from tests.compiling.utils_instructions import MockInstruction


def test_cnot_css_extractor_on_XX_check():
    check = specific_check(['X', 'X'])
    data_qubits = [pauli.qubit for pauli in check.paulis.values()]
    ancilla = Qubit(-1)
    check.ancilla = ancilla

    initialisation_instructions = {State.Plus: ['RX']}
    measurement_instructions = {PauliLetter('X'): ['MX']}
    extractor = CnotCssExtractor(
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
        # Extract first X check
        2: {
            data_qubits[0]: [MockInstruction([ancilla, data_qubits[0]], 'CNOT')],
            ancilla: [MockInstruction([ancilla, data_qubits[0]], 'CNOT')]},
        # Extract second X check
        4: {
            data_qubits[1]: [MockInstruction([ancilla, data_qubits[1]], 'CNOT')],
            ancilla: [MockInstruction([ancilla, data_qubits[1]], 'CNOT')]},
        # Measure ancilla
        6: {
            ancilla: [MockInstruction([ancilla], 'MX', is_measurement=True)]}
    }
    assert circuit.instructions == expected


def test_cnot_css_extractor_on_ZZ_check():
    check = specific_check(['Z', 'Z'])
    data_qubits = [pauli.qubit for pauli in check.paulis.values()]
    ancilla = Qubit(-1)
    check.ancilla = ancilla

    initialisation_instructions = {State.Zero: ['RZ']}
    measurement_instructions = {PauliLetter('Z'): ['MZ']}
    extractor = CnotCssExtractor(
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
        # Extract first X check
        2: {
            data_qubits[0]: [MockInstruction([data_qubits[0], ancilla], 'CNOT')],
            ancilla: [MockInstruction([data_qubits[0], ancilla], 'CNOT')]},
        # Extract second X check
        4: {
            data_qubits[1]: [MockInstruction([data_qubits[1], ancilla], 'CNOT')],
            ancilla: [MockInstruction([data_qubits[1], ancilla], 'CNOT')]},
        # Measure ancilla
        6: {
            ancilla: [MockInstruction([ancilla], 'MZ', is_measurement=True)]}
    }
    assert circuit.instructions == expected

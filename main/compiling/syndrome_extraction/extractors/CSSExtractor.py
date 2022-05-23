from main.building_blocks.Check import Check
from main.building_blocks.Pauli import Pauli
from main.building_blocks.PauliLetter import PauliX, PauliZ
from main.building_blocks.Qubit import Qubit
from main.compiling.Circuit import Circuit
from main.compiling.Gate import Gate
from main.compiling.compilers.Compiler import Compiler
from main.compiling.noise.NoiseModel import NoiseModel
from main.compiling.syndrome_extraction.cnot_order.CNOTOrderer import CNOTOrderer
from main.compiling.syndrome_extraction.extractors.SyndromeExtractor import SyndromeExtractor
from main.enums import State


class CSSExtractor(SyndromeExtractor):
    def __init__(self, cnot_orderer: CNOTOrderer):
        # This extractor is optimised for CSS codes - it just uses CNOTs (no
        # pre- or post-rotation gates), with the control/target ordering
        # corresponding to whether its an X-check or Z-check.
        super().__init__(cnot_orderer)

    def extract_check(
            self, tick: int, check: Check, circuit: Circuit,
            compiler: Compiler, round: int, _=None, __=None):
        # Underscore parameters are just included to make method signature
        # match base class - ignore them.
        pauli_set = {pauli.letter for pauli in check.paulis}
        # Check this really is a CSS code.
        if pauli_set == {PauliX}:
            ancilla_init_state = State.Plus
        elif pauli_set == {PauliZ}:
            ancilla_init_state = State.Zero
        else:
            raise ValueError('Code is not CSS! Can\'t use CssExtractor')

        return super().extract_check(
            tick, check, circuit, compiler, round,
            ancilla_init_state, pauli_set.pop())

    def extract_pauli(
            self, pauli: Pauli, ancilla: Qubit, tick: int,
            circuit: Circuit, noise_model: NoiseModel):
        if pauli is not None:
            if pauli.letter == PauliX:
                # Set ancilla as control, data qubit as target.
                qubits = [ancilla, pauli.qubit]
            elif pauli.letter == PauliZ:
                # Set data qubit as control, ancilla as target.
                qubits = [pauli.qubit, ancilla]
            else:
                raise ValueError('Code is not CSS! Can\'t use CssExtractor')
            circuit.add_gate(tick, Gate(qubits, 'CNOT'))
            noise = noise_model.two_qubit_gate
            if noise is not None:
                circuit.add_noise(tick + 1, noise.gate(qubits))

        return tick + 2

from main.building_blocks.Check import Check
from main.building_blocks.Pauli import Pauli
from main.building_blocks.PauliLetter import PauliZ, PauliX, PauliY
from main.building_blocks.Qubit import Qubit
from main.compiling.Circuit import Circuit
from main.compiling.Gate import Gate
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import ControlledGateOrderer
from main.compiling.syndrome_extraction.extractors.SyndromeExtractor import SyndromeExtractor
from main.enums import State


class PurePauliWordExtractor(SyndromeExtractor):
    def __init__(
            self, controlled_gate_orderer: ControlledGateOrderer,
            extract_checks_in_parallel: bool):
        # This extractor is optimised for codes where every check is a
        # 'pure' pauli word - i.e. just one repeated letter, e.g. surface code
        # (always XX...X or ZZ...Z), repetition code (always ZZ) or
        # tic-tac-toe code (always XX, YY or ZZ). It avoids needing pre-
        # or post-rotation gates, instead just using controlled two qubit
        # gates.
        super().__init__(controlled_gate_orderer, extract_checks_in_parallel)

    def ancilla_init_and_measurement(self, check: Check):
        pauli_set = {pauli.letter for pauli in check.paulis}
        if pauli_set in [{PauliX}, {PauliY}]:
            init_state = State.Plus
            measurement_basis = PauliX
        elif pauli_set == {PauliZ}:
            init_state = State.Zero
            measurement_basis = PauliZ
        else:
            raise ValueError(
                'Check\'s Pauli word isn\'t a single repeated letter! '
                'Can\'t use PurePauliWordExtractor')
        return init_state, measurement_basis

    def extract_pauli_X(
            self, tick: int, pauli: Pauli, ancilla: Qubit,
            circuit: Circuit, noise_model: NoiseModel):
        # Rotate so that this data qubit is effectively in Z basis
        pre_rotate = None
        post_rotate = None
        controlled_gate = Gate([ancilla, pauli.qubit], 'CX')
        return self.extract_pauli_letter(
            tick, pauli, circuit, noise_model, pre_rotate, controlled_gate,
            post_rotate)

    def extract_pauli_Y(
            self, tick: int, pauli: Pauli, ancilla: Qubit,
            circuit: Circuit, noise_model: NoiseModel):
        # Rotate so that this data qubit is effectively in Z basis
        pre_rotate = None
        post_rotate = None
        controlled_gate = Gate([ancilla, pauli.qubit], 'CY')
        return self.extract_pauli_letter(
            tick, pauli, circuit, noise_model, pre_rotate, controlled_gate,
            post_rotate)

    def extract_pauli_Z(
            self, tick: int, pauli: Pauli, ancilla: Qubit,
            circuit: Circuit, noise_model: NoiseModel):
        pre_rotate = None
        post_rotate = None
        controlled_gate = Gate([pauli.qubit, ancilla], 'CNOT')
        return self.extract_pauli_letter(
            tick, pauli, circuit, noise_model, pre_rotate, controlled_gate,
            post_rotate)

from ast import Raise
from main.building_blocks.Check import Check
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ, PauliX, PauliY
from main.building_blocks.Qubit import Qubit
from main.compiling.Circuit import Circuit
from main.compiling.Instruction import Instruction
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import (
    ControlledGateOrderer,
)
from main.compiling.syndrome_extraction.extractors.SyndromeExtractor import (
    SyndromeExtractor,
)
from main.enums import State


class PurePauliWordExtractor(SyndromeExtractor):
    def __init__(
        self,
        controlled_gate_orderer: ControlledGateOrderer,
        extract_checks_in_parallel: bool = True,
    ):
        # This extractor is optimised for codes where every check is a
        # 'pure' pauli word - i.e. just one repeated letter, e.g. surface code
        # (always XX...X or ZZ...Z), repetition code (always ZZ) or
        # tic-tac-toe code (always XX, YY or ZZ). It avoids needing pre-
        # or post-rotation gates, instead just using controlled two qubit
        # gates.
        super().__init__(controlled_gate_orderer, extract_checks_in_parallel)

    def ancilla_init_and_measurement(self, check: Check):
        pauli_set = {pauli.letter for pauli in check.paulis.values()}
        if pauli_set in [{PauliX}, {PauliY}]:
            init_state = State.Plus
            measurement_basis = PauliX
        elif pauli_set == {PauliZ}:
            if "CNOT" in gate_set:
                init_state = State.Zero
                measurement_basis = PauliZ
            elif "CZ" in gate_set:
                init_state = State.Plus
                measurement_basis = PauliX

        else:
            raise ValueError(
                "Check's Pauli word isn't a single repeated letter! "
                "Can't use PurePauliWordExtractor"
            )
        return init_state, measurement_basis

    def extract_pauli_X(
        self,
        tick: int,
        pauli: Pauli,
        ancilla: Qubit,
        circuit: Circuit,
        noise_model: NoiseModel,
        gate_set: set,
    ):
        if "CNOT" in gate_set:
            pre_rotate = None
            post_rotate = None
            controlled_gate = Instruction([ancilla, pauli.qubit], "CNOT")
        elif "CZ" in gate_set:
            if "H" in gate_set:
                pre_rotate = Instruction([pauli.qubit], "H")
                post_rotate = Instruction([pauli.qubit], "H")
            else:
                raise Exception("H needs to be in the gateset")
            controlled_gate = Instruction([ancilla, pauli.qubit], "CZ")
        else:
            raise Exception("CZ or CNOT needs to be in the gate set")
        return self.extract_pauli_letter(
            tick, pauli, circuit, noise_model, pre_rotate, controlled_gate, post_rotate
        )

    def extract_pauli_Y(
        self,
        tick: int,
        pauli: Pauli,
        ancilla: Qubit,
        circuit: Circuit,
        noise_model: NoiseModel,
        gate_set: set,
    ):
        pre_rotate = None
        post_rotate = None
        controlled_gate = Instruction([ancilla, pauli.qubit], "CY")
        return self.extract_pauli_letter(
            tick, pauli, circuit, noise_model, pre_rotate, controlled_gate, post_rotate
        )

    def extract_pauli_Z(
        self,
        tick: int,
        pauli: Pauli,
        ancilla: Qubit,
        circuit: Circuit,
        noise_model: NoiseModel,
        gate_set: set,
    ):
        if "CNOT" in gate_set:
            pre_rotate = None
            post_rotate = None
            controlled_gate = Instruction([pauli.qubit, ancilla], "CNOT")
        elif "CZ" in gate_set:
            pre_rotate = None
            post_rotate = None
            controlled_gate = Instruction([pauli.qubit, ancilla], "CZ")
        else:
            raise Exception("CZ or CNOT needs to be in the gate set")

        return self.extract_pauli_letter(
            tick, pauli, circuit, noise_model, pre_rotate, controlled_gate, post_rotate
        )

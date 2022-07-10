from __future__ import annotations

from typing import TYPE_CHECKING

from main.building_blocks.Check import Check
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ, PauliX, PauliY
from main.building_blocks.Qubit import Qubit
from main.compiling.Circuit import Circuit
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import TrivialOrderer

if TYPE_CHECKING:
    from main.compiling.compilers.Compiler import Compiler
from main.compiling.Instruction import Instruction
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import ControlledGateOrderer
from main.enums import State


# TODO - it might be that a better design just has all these methods within
#  the compiler, and one should override these methods in a compiler subclass.
#  I say this because we currently actually pass in the compiler object to
#  the extract_check method. On the other hand, the argument in favour of this
#  current design is that this extraction seems independent of the compiler -
#  e.g. for the rotated surface code, we usually use an ancilla per plaquette,
#  but if we were feeling funky we could just one ancilla for the whole code
#  and extract syndromes sequentially. In both cases though, the extraction
#  circuits themselves are 'the same' - the only difference is which qubit is
#  the ancilla in each case.
class SyndromeExtractor:
    def __init__(
            self, controlled_gate_orderer: ControlledGateOrderer = None,
            extract_checks_in_parallel: bool = True):
        # This extractor will work for any pauli word stabilizer,
        # but won't necessarily give an optimal circuit.
        if controlled_gate_orderer is None:
            controlled_gate_orderer = TrivialOrderer()
        self.controlled_gate_orderer = controlled_gate_orderer
        self.extract_checks_in_parallel = extract_checks_in_parallel

    def extract_check(
            self, check: Check, round: int, compiler: Compiler,
            tick: int, circuit: Circuit):

        # First initialise the ancilla qubit.
        ancilla_init_state, measurement_basis = \
            self.ancilla_init_and_measurement(check)
        tick = compiler.initialize_qubits(
            {check.ancilla: ancilla_init_state}, tick, circuit)

        # Now place controlled gates between data qubits and the ancilla,
        # possibly with some rotation gates on data qubits too.
        ordered_paulis = self.controlled_gate_orderer.order(check)
        for pauli in ordered_paulis:
            if pauli is None:
                # Leave a gap here in the controlled-gate schedule.
                # TODO - it shouldn't be hardcoded that 6 ticks are needed for
                #  a pre-rotate, controlled gate, then post-rotate, e.g. if
                #  user passes in own native gate set.
                tick += 6
            elif pauli.letter == PauliX:
                tick = self.extract_pauli_X(
                    tick, pauli, check.ancilla, circuit, compiler.noise_model)
            elif pauli.letter == PauliY:
                tick = self.extract_pauli_Y(
                    tick, pauli, check.ancilla, circuit, compiler.noise_model)
            else:
                assert pauli.letter == PauliZ
                tick = self.extract_pauli_Z(
                    tick, pauli, check.ancilla, circuit, compiler.noise_model)

        # Now measure the ancilla to get the check measurement result.
        tick = compiler.measure_qubit(
            check.ancilla, measurement_basis, check, round, tick, circuit)
        return tick

    def ancilla_init_and_measurement(self, check: Check):
        return State.Zero, PauliZ

    def extract_pauli_X(
            self, tick: int, pauli: Pauli, ancilla: Qubit,
            circuit: Circuit, noise_model: NoiseModel):
        # Rotate so that this data qubit is effectively in Z basis
        pre_rotate = Instruction([pauli.qubit], 'H')
        post_rotate = Instruction([pauli.qubit], 'H')
        controlled_gate = Instruction([pauli.qubit, ancilla], 'CNOT')
        return self.extract_pauli_letter(
            tick, pauli, circuit, noise_model, pre_rotate, controlled_gate,
            post_rotate)

    def extract_pauli_Y(
            self, tick: int, pauli: Pauli, ancilla: Qubit,
            circuit: Circuit, noise_model: NoiseModel):
        # Rotate so that this data qubit is effectively in Z basis
        pre_rotate = Instruction([pauli.qubit], 'SQRT_X')
        post_rotate = Instruction([pauli.qubit], 'SQRT_X_DAG')
        controlled_gate = Instruction([pauli.qubit, ancilla], 'CNOT')
        return self.extract_pauli_letter(
            tick, pauli, circuit, noise_model, pre_rotate, controlled_gate,
            post_rotate)

    def extract_pauli_Z(
            self, tick: int, pauli: Pauli, ancilla: Qubit,
            circuit: Circuit, noise_model: NoiseModel):
        pre_rotate = None
        post_rotate = None
        controlled_gate = Instruction([pauli.qubit, ancilla], 'CNOT')
        return self.extract_pauli_letter(
            tick, pauli, circuit, noise_model, pre_rotate, controlled_gate,
            post_rotate)

    def extract_pauli_letter(
            self, tick: int, pauli: Pauli, circuit: Circuit,
            noise_model: NoiseModel, pre_rotate: Instruction | None,
            controlled_gate: Instruction, post_rotate: Instruction | None):
        tick = self.rotate(tick, pauli, pre_rotate, circuit, noise_model)
        circuit.add_instruction(tick, controlled_gate)
        noise = noise_model.two_qubit_gate
        if noise is not None:
            circuit.add_instruction(tick + 1, noise.instruction(controlled_gate.qubits))
        tick += 2
        tick = self.rotate(tick, pauli, post_rotate, circuit, noise_model)
        return tick

    def rotate(
            self, tick: int, pauli: Pauli, rotation_gate: Instruction | None,
            circuit: Circuit, noise_model: NoiseModel):
        if rotation_gate is not None:
            circuit.add_instruction(tick, rotation_gate)
            noise = noise_model.one_qubit_gate
            if noise is not None:
                circuit.add_instruction(tick + 1, noise.instruction([pauli.qubit]))
        return tick + 2

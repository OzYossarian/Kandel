from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Iterable, Callable, TYPE_CHECKING

from main.building_blocks.Check import Check
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.pauli.utils import plus_one_eigenstates
from main.compiling.Circuit import Circuit
from main.compiling.Instruction import Instruction
if TYPE_CHECKING:
    from main.compiling.compilers.Compiler import Compiler
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import ControlledGateOrderer
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import TrivialOrderer
from main.enums import State
from main.utils.types import Tick


class SyndromeExtractor(ABC):
    def __init__(
            self, controlled_gate_orderer: ControlledGateOrderer = None,
            initialisation_instructions: Dict[State, List[str]] = None,
            measurement_instructions: Dict[PauliLetter, List[str]] = None,
            parallelize: bool = True):
        if controlled_gate_orderer is None:
            controlled_gate_orderer = TrivialOrderer()
        self.controlled_gate_orderer = controlled_gate_orderer
        self.parallelize = parallelize

        # If the instructions below are `None`, we'll just use the same
        # instructions that the compiler uses.
        self.initialisation_instructions = initialisation_instructions
        self.measurement_instructions = measurement_instructions

    def extract_checks(
            self,
            checks: Iterable[Check],
            round: int,
            tick: int,
            circuit: Circuit,
            compiler: Compiler) -> Tick:

        # If initialisation instructions are None, this means we should just
        # use the ones the compiler uses.
        initialisation_instructions = self.initialisation_instructions \
            if self.initialisation_instructions is not None \
            else compiler.initialisation_instructions

        # Same for measurement instructions.
        measurement_instructions = self.measurement_instructions \
            if self.measurement_instructions is not None \
            else compiler.measurement_instructions

# <<<<<<< HEAD
        if self.parallelize:
            return self._extract_checks_in_parallel(
                checks, round, tick, circuit, compiler,
                initialisation_instructions, measurement_instructions)
        else:
            return self._extract_checks_in_sequence(
                checks, round, tick, circuit, compiler,
                initialisation_instructions, measurement_instructions)

    def _extract_checks_in_parallel(
            self,
            checks: Iterable[Check],
            round: int,
            tick: int,
            circuit: Circuit,
            compiler: Compiler,
            initialisation_instructions: Dict[State, List[str]],
            measurement_instructions: Dict[PauliLetter, List[str]]) -> Tick:
        # Important to keep the controlled gates in sync here, despite
        # potentially varying numbers of gates used for initialising into
        # different bases, rotating a data qubit ahead of a control gate, etc.

        # First initialise all ancillas and return the next usable tick
        initial_states = {}
        ancilla_bases = []
        for check in checks:
            ancilla_basis = self.get_ancilla_basis(check)
            # Measurement at the end will use the same basis, so note it down
            ancilla_bases.append(ancilla_basis)
            initial_state = plus_one_eigenstates[ancilla_basis]
            initial_states[check.ancilla] = initial_state
        tick = compiler.initialize_qubits(
            initial_states, tick, circuit, initialisation_instructions)

        ordered_paulis = [
            self.controlled_gate_orderer.order(check)
            for check in checks]
        # Each item in `ordered_paulis` should be a list of type
        # `Pauli | None` of the same length
        lengths = {len(order) for order in ordered_paulis}
        assert len(lengths) == 1
        steps = lengths.pop()

        # Now extract each of the Paulis of each check in turn
        for step in range(steps):
            tick = self.extract_step(
                step, checks, ordered_paulis, tick, circuit, compiler)

        # Finally, measure the ancilla qubits.
        paulis = (
            Pauli(check.ancilla, basis)
            for check, basis in zip(checks, ancilla_bases))
        tick = compiler.measure_qubits(
            paulis, checks, round, tick, circuit, measurement_instructions)

        return tick

    def _extract_checks_in_sequence(
            self,
            checks: Iterable[Check],
            round: int,
            tick: int,
            circuit: Circuit,
            compiler: Compiler,
            initialisation_instructions: Dict[State, List[str]],
            measurement_instructions: Dict[PauliLetter, List[str]]) -> Tick:
        # Simple enough to use the existing code here:
        for check in checks:
            tick = self._extract_checks_in_parallel(
                [check], round, tick, circuit, compiler,
                initialisation_instructions, measurement_instructions)
        return tick

    def extract_step(
            self,
            step: int,
            checks: Iterable[Check],
            ordered_paulis: Iterable[List[Pauli | None]],
            tick: int,
            circuit: Circuit,
            compiler: Compiler) -> Tick:
        # Get just the Paulis that are actually involved at this step.
        paulis = [paulis[step] for paulis in ordered_paulis]

        # First, pre-rotate data qubits.
        # `next_tick` means "the one at which we should do the controlled
        # gates". Each data qubit might require a different number of gates
        # in order to be rotated; we want the next tick to be the soonest even
        # one after ALL of these rotations are done.
        next_tick = tick
        for check, pauli in zip(checks, paulis):
            tick_after_rotation = self.pre_rotate_pauli(
                pauli, check, tick, circuit, compiler)
            next_tick = max(next_tick, tick_after_rotation)
        tick = next_tick

        # Next, do the controlled gate between the data and ancilla qubits.
        for check, pauli in zip(checks, paulis):
            self.do_control_gate(pauli, check, tick, circuit, compiler)
        # Controlled gates are guaranteed to only take two ticks.
# =======
#     def extract_check(
#         self, check: Check, round: int, compiler: Compiler, tick: int, circuit: Circuit
#     ):
#         # First initialise the ancilla qubit.
#         ancilla_init_state, measurement_basis = self.ancilla_init_and_measurement(
#             check, compiler.gate_set
#         )
#         tick = compiler.initialize_qubits(
#             {check.ancilla: ancilla_init_state}, tick, circuit
#         )
#
#         # Now place controlled gates between data qubits and the ancilla,
#         # possibly with some rotation gates on data qubits too.
#         ordered_paulis = self.controlled_gate_orderer.order(check)
#         for pauli in ordered_paulis:
#             if pauli is None:
#                 # Leave a gap here in the controlled-gate schedule.
#                 # TODO - it shouldn't be hardcoded that 6 ticks are needed for
#                 #  a pre-rotate, controlled gate, then post-rotate, e.g. if
#                 #  user passes in own native gate set.
#                 tick += 6
#             elif pauli.letter == PauliX:
#                 tick = self.extract_pauli_X(
#                     tick,
#                     pauli,
#                     check.ancilla,
#                     circuit,
#                     compiler.noise_model,
#                     compiler.gate_set,
#                 )
#             elif pauli.letter == PauliY:
#                 tick = self.extract_pauli_Y(
#                     tick,
#                     pauli,
#                     check.ancilla,
#                     circuit,
#                     compiler.noise_model,
#                     compiler.gate_set,
#                 )
#             else:
#                 assert pauli.letter == PauliZ
#                 tick = self.extract_pauli_Z(
#                     tick,
#                     pauli,
#                     check.ancilla,
#                     circuit,
#                     compiler.noise_model,
#                     compiler.gate_set,
#                 )
#
#         # Now measure the ancilla to get the check measurement result.
#         tick = compiler.measure_qubit(
#             check.ancilla, measurement_basis, check, round, tick, circuit
#         )
#         return tick
#
#     def ancilla_init_and_measurement(self, check: Check, gate_set: set):
#         return State.Zero, PauliZ
#
#     def extract_pauli_X(
#         self,
#         tick: int,
#         pauli: Pauli,
#         ancilla: Qubit,
#         circuit: Circuit,
#         noise_model: NoiseModel,
#     ):
#         # Rotate so that this data qubit is effectively in Z basis
#         pre_rotate = Instruction([pauli.qubit], "H")
#         post_rotate = Instruction([pauli.qubit], "H")
#         controlled_gate = Instruction([pauli.qubit, ancilla], "CNOT")
#         return self.extract_pauli_letter(
#             tick, pauli, circuit, noise_model, pre_rotate, controlled_gate, post_rotate
#         )
#
#     def extract_pauli_Y(
#         self,
#         tick: int,
#         pauli: Pauli,
#         ancilla: Qubit,
#         circuit: Circuit,
#         noise_model: NoiseModel,
#     ):
#         # Rotate so that this data qubit is effectively in Z basis
#         pre_rotate = Instruction([pauli.qubit], "SQRT_X")
#         post_rotate = Instruction([pauli.qubit], "SQRT_X_DAG")
#         controlled_gate = Instruction([pauli.qubit, ancilla], "CNOT")
#         return self.extract_pauli_letter(
#             tick, pauli, circuit, noise_model, pre_rotate, controlled_gate, post_rotate
#         )
#
#     def extract_pauli_Z(
#         self,
#         tick: int,
#         pauli: Pauli,
#         ancilla: Qubit,
#         circuit: Circuit,
#         noise_model: NoiseModel,
#     ):
#         pre_rotate = None
#         post_rotate = None
#         controlled_gate = Instruction([pauli.qubit, ancilla], "CNOT")
#         return self.extract_pauli_letter(
#             tick, pauli, circuit, noise_model, pre_rotate, controlled_gate, post_rotate
#         )
#
#     def extract_pauli_letter(
#         self,
#         tick: int,
#         pauli: Pauli,
#         circuit: Circuit,
#         noise_model: NoiseModel,
#         pre_rotate: Instruction | None,
#         controlled_gate: Instruction,
#         post_rotate: Instruction | None,
#     ):
#         tick = self.rotate(tick, pauli, pre_rotate, circuit, noise_model)
#         circuit.add_instruction(tick, controlled_gate)
#         noise = noise_model.two_qubit_gate
#         if noise is not None:
#             circuit.add_instruction(tick + 1, noise.instruction(controlled_gate.qubits))
# >>>>>>> dev
        tick += 2

        # Finally, post-rotate data qubits.
        next_tick = tick
        for check, pauli in zip(checks, paulis):
            tick_after_rotation = self.post_rotate_pauli(
                pauli, check, tick, circuit, compiler)
            next_tick = max(next_tick, tick_after_rotation)
        tick = next_tick

        return tick

    def pre_rotate_pauli(
            self,
            pauli: Pauli | None,
            check: Check,
            tick: int,
            circuit: Circuit,
            compiler: Compiler) -> Tick:
        return self._rotate_pauli(
            pauli, check, self.get_pre_rotations, tick, circuit, compiler)

    def post_rotate_pauli(
            self,
            pauli: Pauli | None,
            check: Check,
            tick: int,
            circuit: Circuit,
            compiler: Compiler) -> Tick:
        return self._rotate_pauli(
            pauli, check, self.get_post_rotations, tick, circuit, compiler)

    def _rotate_pauli(
            self,
            pauli: Pauli | None,
            check: Check,
            get_rotations: Callable[[Pauli, Check], List[Instruction]],
            tick: int,
            circuit: Circuit,
            compiler: Compiler) -> Tick:
        if pauli is None:
            # Nothing to do for this check at this step.
            return tick
        pre_rotations = get_rotations(pauli, check)
        tick = compiler.compile_one_qubit_gates(
            pre_rotations, tick, circuit)
        return tick

    def do_control_gate(
            self,
            pauli: Pauli | None,
            check: Check,
            tick: int,
            circuit: Circuit,
            compiler: Compiler):
        # Only something to do if the Pauli at this step is not None.
        if pauli is not None:
            control_gate = self.get_control_gate(pauli, check)
            compiler.compile_two_qubit_gates([control_gate], tick, circuit)

    @abstractmethod
    def get_ancilla_basis(self, check: Check) -> PauliLetter:
        raise NotImplementedError("Must be overridden in a subclass!")

    @abstractmethod
    def get_pre_rotations(
            self, pauli: Pauli, check: Check) -> List[Instruction]:
        raise NotImplementedError("Must be overridden in a subclass!")

    @abstractmethod
    def get_post_rotations(
            self, pauli: Pauli, check: Check) -> List[Instruction]:
        raise NotImplementedError("Must be overridden in a subclass!")

    @abstractmethod
    def get_control_gate(self, pauli: Pauli, check: Check) -> Instruction:
        raise NotImplementedError("Must be overridden in a subclass!")

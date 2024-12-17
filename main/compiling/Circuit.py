from collections import defaultdict
from typing import List, Dict, Tuple, Any, Iterable, Union

import stim
import stimcirq
from alive_progress import alive_bar

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.compiling.Instruction import Instruction
from main.compiling.Measurer import Measurer
from main.compiling.noise.noises import OneQubitNoise
from main.utils.types import Tick

RepeatBlock = Union[Tuple[int, int, int], None]


class Circuit:
    def __init__(self):
        """Intermediate representation of a quantum circuit. Rather than
        compile directly to a Stim circuit, which is somewhat inflexible, we
        first compile to our own Circuit class. One should picture a circuit
        diagram - that is, a 2D lattice, with gates placed on vertices. Time
        flows left to right, so each horizontal line represents a qubit.

        Gates, noise, detectors, etc are all types of 'instructions'. All
        noise EXCEPT idling noise is included in the circuit diagram: idling
        noise is added in right before the Circuit is compiled further to an
        actual Stim circuit.

        At a given location (tick, qubit) in the circuit, only one gate can
        occur. But multiple noise instructions can exist at a single site -
        e.g. noise arising because a single qubit gate was just performed,
        plus noise arising because we're about to perform a measurement.
        """
        # The core of this class is a nested dictionary of instructions,
        # keyed first by tick, then by qubit. Values are then lists of
        # instructions acting on that qubit at that tick.
        self.instructions: Dict[Tick, Dict[Qubit, List[Instruction]]] = defaultdict(
            lambda: defaultdict(list)
        )
        # Maintain a set of all the qubits we've come across - used when
        # adding idle noise later.
        self.qubits = set()
        # Each qubit will ultimately be assigned an integer index in stim.
        self._qubit_indexes = {}
        # Track at which ticks qubits were initialised and measured, so we
        # say whether a qubit is currently initialised or not.
        self.init_ticks: Dict[Qubit, List[Tick]] = defaultdict(list)
        self.measure_ticks: Dict[Qubit, List[Tick]] = defaultdict(list)
        self.shift_ticks = []
        # For each tick, note whether it's inside a repeat block.
        self.repeat_blocks: Dict[int, RepeatBlock] = defaultdict(lambda: None)
        # Track which measurements tell us the value of which checks
        self.measurer = Measurer()
        # Annoying extra hoops to jump through to get the targets for
        # Pauli product measurements.
        self.pauli_targeters = {
            'X': stim.target_x,
            'Y': stim.target_y,
            'Z': stim.target_z}

        
    def to_cirq_string(self, idling_noise: OneQubitNoise = None) -> str:
        """Represents an instance of this class as cirq ascii circuit, useful for debugging

        Args:
            idling_noise:
                a noise model which contains the noise channel to apply to
                idling qubits. Defaults to None.

        Returns:
            str : a drawing of the circuit generated using cirq.
        """
        return str(stimcirq.stim_circuit_to_cirq_circuit(self.to_stim(idling_noise)))

    def number_of_instructions(self, instruction_names: Iterable[str]) -> int:
        """Counts the number of times an instruction occurs.

        Args:
            instruction_names: Names of the instructions to count.

        Returns:
            Number of occurrences of instructions with these names.
        """
        occurrences = 0
        for instructions_at_tick in self.instructions.values():
            for instructions_on_qubit_at_tick in instructions_at_tick.values():
                for instruction in instructions_on_qubit_at_tick:
                    if instruction.name in instruction_names:
                        occurrences += 1
        return occurrences

    def qubit_index(self, qubit: Qubit) -> int:
        """Get the stim index corresponding to this qubit, or create one if it doesn't yet have one.

        Args:
            qubit: Qubit to get the index of.

        Returns:
            Integer which is the index of the qubit in stim.
        """
        if qubit in self._qubit_indexes:
            index = self._qubit_indexes[qubit]
        else:
            index = len(self._qubit_indexes)
            self._qubit_indexes[qubit] = index
        return index

    def is_initialised(self, tick: Tick, qubit: Qubit) -> bool:
        """At this tick, return whether this qubit has been initialised but not yet measured out

        Args:
            tick: Tick at which to check if a qubit is initialised
            qubit: The qubit which is being checked.

        Returns:
            True if the qubit is initialised and false if not.
        """
        inits = [t for t in sorted(self.init_ticks[qubit]) if t <= tick]
        measures = [t for t in sorted(self.measure_ticks[qubit]) if t <= tick]
        inits_max = inits[-1] if len(inits) > 0 else -1
        measures_max = measures[-1] if len(measures) > 0 else -1
        return inits_max > measures_max

    def initialise(self, tick: Tick, instruction: Instruction):
        """Initialise a qubit at a specific tick

        Args:
            tick: Tick at which to add the initialization to.
            instruction: The initialization instruction. It has to apply to a single qubit
                and its name must start with "R".
        """
        # Initialise a single qubit..
        if len(instruction.qubits) != 1:
            raise ValueError("The instruction has to act on 1 qubit")
        qubit = instruction.qubits[0]
        if instruction.name[0] != "R":
            raise ValueError(
                "The instruction has to be an initialize instruction starting with \"R\"")
        self.add_instruction(tick, instruction)
        # Note down at which tick this qubit is considered initialised.
        self.init_ticks[qubit].append(tick)

    def end_round(self, tick: int):
        self.shift_ticks.append(tick)

    def measure(self, measurement: Instruction, check: Check, round: int, tick: int):
        """Adds a measurement instruction to the circuit

        In addition to updating the circuit, the properties of the
        measurement class are updated such that the detector
        can be added to the stim circuit when running to_stim()

        Args:
            measurement:
                Measurement instruction, which can be on one or multiple
                qubits.
            check:
                The check to which the measurement corresponds.
                This is used by the measurer class to compile detectors.
            round:
                The QEC round in which the measurement takes place.
                This is used by the measurer class to compile detectors.
            tick:
                Tick at which the measurement happens.
        """
        # TODO - raise error if measurement.is_measurement is False?
        # Measure a qubit (perhaps multiple)
        self.add_instruction(tick, measurement)
        # If the measurement is not a Pauli product measurement, 
        # then this is a single qubit measurement which measures out the qubit.
        # Record that these qubits have been measured.
        if measurement.name != "MPP":
            for qubit in measurement.qubits:
                self.measure_ticks[qubit].append(tick)
        # Note down that this instruction corresponds to the measurement of a
        # particular check in a particular round. This info is used when
        # compiling detectors later.
        self.measurer.add_measurement(measurement, check, round)

    def add_instruction(self, tick: int, instruction: Instruction):
        """Adds an instruction to the Circuit

        Args:
            tick:
                Tick at which the instruction should be added.
            instruction:
                Instruction to be added to the circuit.

        Raises:
            ValueError:
                If trying to place a noise instruction at an even tick, or a
                non-noise instruction at an odd tick, or if there is already
                an instruction on the same qubit(s) at this tick.

        Note:
            Don't use this function for initializing a qubit or for
            measuring a qubit. For measuring use Circuit.measure and for
            initializing use Circuit.initialize.
        """
        # TODO - if instruction starts with 'R' or 'M', raise an error?
        # Even ticks are for gates, odd ticks are for noise.
        if instruction.is_noise and tick % 2 == 0:
            raise ValueError(
                f"Can't place a noise instruction at an even tick! "
                f"This really shouldn't have happened; it's probably a bug. "
                f"Tried to place instruction {instruction} at tick {tick}")
        elif not instruction.is_noise and tick % 2 == 1:
            raise ValueError(
                f"Can't place a non-noise instruction at an odd tick! "
                f"This really shouldn't have happened; it's probably a bug. "
                f"Tried to place instruction {instruction} at tick {tick}")

        for qubit in instruction.qubits:
            instructions_on_qubit_at_tick = self.instructions[tick][qubit]
            if len(instructions_on_qubit_at_tick) > 0:
                # Only time a qubit can have multiple gates at the same tick
                # is when they're all noise gates or all Pauli product
                # measurements - check this isn't violated.
                instructions = instructions_on_qubit_at_tick + [instruction]
                all_noise = all([
                    instruction.is_noise for instruction in instructions])
                all_product_measurements = all([
                    instruction.name == "MPP" for instruction in instructions])
                if not (all_noise or all_product_measurements):
                    # Can't add this instruction to the circuit!
                    instructions_string = "\n".join([
                        str(instruction) for instruction in instructions])
                    raise ValueError(
                        f"Tried to compile conflicting instructions on qubit "
                        f"{qubit} at tick {tick}! "
                        f"Instructions are:\n {instructions_string}")

            # Otherwise, no problem - add this instruction to the circuit.
            instructions_on_qubit_at_tick.append(instruction)
            # Add this to the set of qubits we've come across in the circuit.
            self.qubits.add(qubit)

    def add_repeat_block(self, start: Tick, end: Tick, repeats: int):
        # start inclusive, end exclusive.
        # Check this repeat block is well-defined - isn't trivial and doesn't
        # overlap with other repeat blocks.
        if start >= end:
            raise ValueError(
                f"Repeat block must contain at least one tick! "
                f"Instead, requested a repeat block from tick {start} "
                f"(inclusive) to tick {end} (exclusive).")
        if repeats < 1:
            raise ValueError(
                f"Repeat block must repeat at least once! Instead, "
                f"requested a repeat block that repeats {repeats} times.")
        existing_repeat_blocks = {
            tick: self.repeat_blocks[tick] for tick in range(start, end)}
        conflicting_repeat_blocks = any([
            block is not None for block in existing_repeat_blocks.values()])
        if conflicting_repeat_blocks:
            raise ValueError(
                f"Can't compile conflicting repeat blocks. Requested a repeat "
                f"block from {start} to {end} that repeats {repeats} times, "
                f"but on these ticks we already have the following repeat "
                f"blocks, denoted by (start, end, repeats) tuples: "
                f"{existing_repeat_blocks}.")
        for i in range(start, end):
            self.repeat_blocks[i] = (start, end, repeats)

    def compress(self):
        # Return a copy of this circuit with unnecessary idle time removed.
        # TODO - implement!
        raise NotImplementedError

    def add_idling_noise(self, idling_noise: Union[OneQubitNoise, None]):
        """Adds idling noise everywhere in the circuit

        Idling noise is added at every tick to qubits that have been
        initialized but on which no non-identity gate is performed

        Args:
            idling_noise:
                Noise channel to apply to idling locations in the circuit.
        """

        # If circuit is going to be compressed, then this should be done
        # before adding idling noise, since compression changes the amount
        # of idling time in the circuit.
        if idling_noise is not None:
            # Note that this only loop through ticks at which there is at
            # least one instruction
            for tick in sorted(self.instructions.keys()):
                # Only interested in even ticks, where actual gates happen.
                if tick % 2 == 0:
                    # Find out which qubits were idle at this tick. These are
                    # those that are initialised but not involved in any gate.
                    idle_qubits = self.get_idle_qubits(tick)
                    # Sort for reproducibility in tests.
                    idle_qubits = sorted(
                        idle_qubits, key=lambda qubit: qubit.coords)
                    for qubit in idle_qubits:
                        noise = idling_noise.instruction([qubit])
                        self.add_instruction(tick + 1, noise)

    def get_idle_qubits(self, tick: Tick):
        # A qubit is idle at a given tick if it has been initialised but
        # isn't involved in any non-identity gate.
        def is_active(instructions: List[Instruction]):
            names = [instruction.name for instruction in instructions]
            return names not in [[], ['I']]

        initialised_qubits = {
            qubit
            for qubit in self.qubits
            if self.is_initialised(tick, qubit)}
        active_qubits = {
            qubit for qubit, instructions
            in self.instructions[tick].items()
            if is_active(instructions)}
        idle_qubits = initialised_qubits.difference(active_qubits)
        return idle_qubits

    def to_stim(
        self,
        idling_noise: Union[OneQubitNoise, None],
        track_coords: bool = True,
        track_progress: bool = True,
    ) -> stim.Circuit:
        """Transforms the circuit to a stim circuit.

        Args:
            idling_noise: Noise channel to apply to idling locations in the circuit. Note that using to_stim will only
                add idling noise.
            track_coords: Whether to track the coordinates of the qubits and detectors. Defaults to True.
            track_progress: If this is set to True a progress bar is printed. The progress bar shows how many ticks
                have been translated and the time taken. Defaults to True.

        Returns:
            The resulting stim circuit.

        """
        if track_progress:
            # TODO - bug here: sometimes this progress bar overfills!
            with alive_bar(len(self.instructions), force_tty=True) as bar:
                return self._to_stim(idling_noise, track_coords, bar)
        else:
            return self._to_stim(idling_noise, track_coords, None)

    def _to_stim(
        self, idling_noise: Union[OneQubitNoise, None], track_coords: bool, progress_bar: Any
    ) -> stim.Circuit:
        """Called by to_stim() to transform the circuit to a stim circuit.

        Args:
            idling_noise: Noise channel to apply to idling locations in the circuit.
            track_coords: Whether to track the coordinates of the qubits and detectors.
            progress_bar: An alive progress bar, if tracking progress. Else, None.

        Returns:
            the resulting stim circuit.
        """
        # Figure out which temporal dimension to shift if tracking coords.
        if track_coords:
            qubit_dimensions = {qubit.dimension for qubit in self.qubits}
            assert len(qubit_dimensions) == 1
            dimension = qubit_dimensions.pop()
            shift_coords = tuple([0 for _ in range(dimension)] + [1])
        else:
            shift_coords = None

        # Go through the circuit and add idling noise.
        self.add_idling_noise(idling_noise)

        # Track which instructions have been compiled to stim.
        compiled = defaultdict(bool)

        # Let 'circuit' denote the circuit we're currently compiling to - if
        # using repeat blocks, this need not always be the full circuit itself
        full_circuit = stim.Circuit()
        circuit = full_circuit

        most_recent_tick = -1
        final_tick = max(self.instructions.keys())
        if track_coords:
            for qubit in sorted(self.qubits, key=lambda qubit: qubit.coords):
                index = self.qubit_index(qubit)
                circuit.append("QUBIT_COORDS", [index], qubit.coords)

        for tick, qubit_instructions in sorted(self.instructions.items()):
            # Check whether we need to close a repeat block
            repeats = self.left_repeat_block(tick, most_recent_tick)
            if repeats is not None:
                repeat_circuit = stim.CircuitRepeatBlock(repeats, circuit)
                full_circuit.append(repeat_circuit)
                circuit = full_circuit
            # Then check whether we need to start a new repeat block
            if self.entered_repeat_block(tick, most_recent_tick):
                circuit = stim.Circuit()

            # Now actually compile instructions at this tick
            measurements = []
            for qubit, instructions in qubit_instructions.items():
                for instruction in instructions:
                    if not compiled[instruction]:
                        self.instruction_to_stim(instruction, circuit)
                        if instruction.is_measurement:
                            measurements.append(instruction)
                        compiled[instruction] = True

            # Let the measurer determine if these measurements trigger any
            # further instructions - e.g. compiling detectors, adding checks
            # into observables, etc.
            further_instructions = (
                self.measurer.measurement_triggers_to_stim(
                    measurements, shift_coords
                )
            )
            for instruction in further_instructions:
                circuit.append(instruction)

            most_recent_tick = tick
            if progress_bar is not None:
                progress_bar()

            if most_recent_tick in self.shift_ticks:
                circuit.append(
                    stim.CircuitInstruction("SHIFT_COORDS", (), shift_coords)
                )

            if tick != final_tick:
                circuit.append("TICK")

        # If we've finished inside a repeat block, close it.
        repeat_block = self.repeat_blocks[final_tick]
        if repeat_block is not None:
            start, end, repeats = repeat_block
            repeat_circuit = stim.CircuitRepeatBlock(repeats, circuit)
            full_circuit.append(repeat_circuit)

        self.measurer.reset_compilation()
        return full_circuit

    def instruction_to_stim(self, instruction: Instruction, circuit: stim.Circuit):
        """Adds an individual Instruction to a circuit

        Args:
            instruction: The instruction to be translated
            circuit: A stim circuit to add the instruction to.
        """
        if instruction.targets is not None:
            targets = instruction.targets
        elif instruction.name == "MPP":
            # Stim's strange syntax for these means we need to 
            # retrieve the check associated to this instruction, 
            # in order to set the targets correctly.
            check, _ = self.measurer.measurement_checks[instruction]
            targets = self.product_measurement_targets(check)
        else:
            targets = [self.qubit_index(qubit) for qubit in instruction.qubits]
        circuit.append(instruction.name, targets, instruction.params)

    def product_measurement_targets(self, check: Check) -> List[stim.GateTarget]:
        """
        Get the Stim measurement targets for the given check, using native
        Pauli product measurement. e.g. An XYZ check on qubits 0, 1 and 2
        has targets X0 * Y1 * Z2

        Args:
            check: check to measure
            circuit: circuit implementing the code so far

        Returns:
            the Stim targets for the check
        """
        # Do first pauli separately, then do the rest in a for loop.
        # We only care about the non-identity ones.
        paulis = [
            pauli for pauli in check.paulis.values()
            if pauli.letter.letter != 'I']
        # We're guaranteed that there's at least one non-identity Pauli,
        # because we enforce this on the Check class
        pauli = paulis[0]
        targeter = self.pauli_targeters[pauli.letter.letter]
        # We're guaranteed the check's product has sign in [1, -1], because
        # we force all checks to have a Hermitian product.
        invert = check.product.word.sign == -1
        # If inverting, it applies to the whole product, but equivalently can
        # just invert one qubit - may as well pick the first one.
        targets = [targeter(self.qubit_index(pauli.qubit), invert)]
        for pauli in paulis[1:]:
            targets.append(stim.target_combiner())
            targeter = self.pauli_targeters[pauli.letter.letter]
            targets.append(targeter(self.qubit_index(pauli.qubit)))
        return targets


    def entered_repeat_block(self, tick: int, last_tick: int):
        """Checks if a repeat block started between last_tick and tick.

        Whether we've entered a repeat block between two CONSECUTIVE ticks.
        That is, if one were to make an ordered list of all ticks at which
        at least one gate occurs, then `tick` and `last_tick` should be
        adjacent in this list. So they need not actually be consecutive
        integers, but if they aren't, then there can be no gates at any tick
        inbetween these two integers.

        Args:
            tick:
                The current tick.
            last_tick:
                The last tick at which at least one gate occurred before
                the current tick.

        Returns:
            Whether we've entered a repeat block between `last_tick` and `tick`.

        """
        last_block = self.repeat_blocks[last_tick]
        this_block = self.repeat_blocks[tick]
        return last_block != this_block and this_block is not None

    def left_repeat_block(self, tick: int, last_tick: int):
        """Returns a repeat blocks repititions if it has ended at last tick.

        Whether we've left a repeat block between two CONSECUTIVE ticks.
        That is, if one were to make an ordered list of all ticks at which
        at least one gate occurs, then `tick` and `last_tick` should be
        adjacent in this list. So they need not actually be consecutive
        integers, but if they aren't, then there can be no gates at any tick
        inbetween these two integers.

        Args:
            tick:
                The current tick.
            last_tick:
                The last tick at which at least one gate occurred before
                the current tick.

        Returns:
            If we have indeed left a repeat block between `last_tick` and
            `tick`, then we return the number of times that repeat block
            should be repeated. Else, we return None.
        """
        last_block = self.repeat_blocks[last_tick]
        this_block = self.repeat_blocks[tick]
        if this_block != last_block and last_block is not None:
            start, end, repeats = last_block
            return repeats
        else:
            return None

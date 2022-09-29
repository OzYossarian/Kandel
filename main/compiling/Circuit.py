from collections import defaultdict
from typing import List, Dict, Tuple, Any

import stim
import stimcirq
from alive_progress import alive_bar

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.compiling.Instruction import Instruction
from main.compiling.Measurer import Measurer
from main.compiling.noise.noises import OneQubitNoise

RepeatBlock = Tuple[int, int, int] | None


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
        self.instructions: Dict[int, Dict[Qubit, List[Instruction]]] = defaultdict(
            lambda: defaultdict(list)
        )
        # Maintain a set of all the qubits we've come across - used when
        # adding idle noise later.
        self.qubits = set()
        # Each qubit will ultimately be assigned an integer index in stim.
        self.qubit_indexes = {}
        # Track at which ticks qubits were initialised and measured, so we
        # say whether a qubit is currently initialised or not.
        self.init_ticks = defaultdict(list)
        self.measure_ticks = defaultdict(list)
        self.shift_ticks = []
        # For each tick, note whether it's inside a repeat block.
        self.repeat_blocks: Dict[int, RepeatBlock] = defaultdict(lambda: None)
        # Track which measurements tell us the value of which checks
        self.measurer = Measurer()

    def to_cirq_string(self, idling_noise: OneQubitNoise | None = None) -> str:
        """Represents an instance of this class as cirq ascii circuit, useful for debugging

        Args:
            idling_noise (OneQubitNoise | None, optional): a noise model which contains the noise channel to apply to idling qubits.
                                                           Defaults to None.

        Returns:
            str : a drawing of the circuit generated using cirq.
        """
        return str(stimcirq.stim_circuit_to_cirq_circuit(self.to_stim(idling_noise)))

    def get_number_of_occurences_of_gate(self, instruction_name: str) -> int:
        """Counts the number of times a gate occurs.

        Args:
            instruction_name (str): Name of the gate to count.

        Returns:
            int: Number of occurences of the gate.
        """
        number_of_occurences = 0
        for instructions_at_tick in self.instructions.values():
            for instructions_on_qubit_at_tick in instructions_at_tick.values():
                for instruction in instructions_on_qubit_at_tick:
                    if instruction.name == instruction_name:
                        number_of_occurences += 1
        return number_of_occurences

    def qubit_index(self, qubit: Qubit):
        # Get the stim index corresponding to this qubit, or create one if
        # it doesn't yet have one.
        if qubit in self.qubit_indexes:
            index = self.qubit_indexes[qubit]
        else:
            index = len(self.qubit_indexes)
            self.qubit_indexes[qubit] = index
        return index

    def is_initialised(self, tick: int, qubit: Qubit):
        # At this tick, return whether this qubit has been initialised
        # but not yet measured
        inits = [t for t in sorted(self.init_ticks[qubit]) if t <= tick]
        measures = [t for t in sorted(self.measure_ticks[qubit]) if t <= tick]
        return max(inits, default=-1) > max(measures, default=-1)

    def initialise(self, tick: int, instruction: Instruction):
        # Initialise a single qubit..
        assert len(instruction.qubits) == 1
        qubit = instruction.qubits[0]
        assert instruction.name[0] == "R"
        self.add_instruction(tick, instruction)
        # Note down at which tick this qubit is considered initialised.
        self.init_ticks[qubit].append(tick)

    def end_round(self, tick: int):
        self.shift_ticks.append(tick)

    def measure(self, measurement: Instruction, check: Check, round: int, tick: int):
        # Measure a qubit (perhaps multiple)
        self.add_instruction(tick, measurement)
        # Record that these qubits have been measured.
        for qubit in measurement.qubits:
            self.measure_ticks[qubit].append(tick)
        # Note down that this gate corresponds to the measurement of a
        # particular check in a particular round. This info is used when
        # building detectors later.
        self.measurer.add_measurement(measurement, check, round)

    def add_instruction(self, tick: int, instruction: Instruction):
        """Adds an instruction to the Circuit

        Args:
            tick (int): Tick at which the instruction should be added.
            instruction (Instruction): Instruction to be added to the circuit.

        Raises:
            ValueError: If there is already an instruction on the same qubit at the tick

        Note:
            Don't use this function for initializing a qubit or for measuring a qubit.
            For measuring use Circuit.measure and for initializing use Circuit.initialize.
        """
        # Even ticks are for gates, odd ticks are for noise.
        assert tick % 2 == (1 if instruction.is_noise else 0)
        for qubit in instruction.qubits:
            instructions_on_qubit_at_tick = self.instructions[tick][qubit]
            instructions_on_qubit_at_tick.append(instruction)
            if len(instructions_on_qubit_at_tick) > 1:
                # Only time a qubit can have multiple gates at the same tick
                # is when they're all noise gates or all Pauli product
                # measurements.
                all_noise = all(
                    [
                        instruction.is_noise
                        for instruction in instructions_on_qubit_at_tick
                    ]
                )
                all_product_measurements = all(
                    [
                        instruction.name == "MPP"
                        for instruction in instructions_on_qubit_at_tick
                    ]
                )
                if not (all_noise or all_product_measurements):
                    instructions_string = "\n".join(
                        [
                            str(instruction)
                            for instruction in instructions_on_qubit_at_tick
                        ]
                    )
                    raise ValueError(
                        f"Tried to compile conflicting instructions on qubit "
                        f"{qubit.coords} at pseudo-tick {tick}! Instructions "
                        f"are:\n {instructions_string}"
                    )
            # Add this to the set of qubits we've come across in the circuit.
            self.qubits.add(qubit)

    def add_repeat_block(self, start: int, end: int, repeats: int):
        # start inclusive, end exclusive.
        # Check this repeat block is well-defined - isn't trivial and doesn't
        # overlap with other repeat blocks.
        assert start + 1 < end
        assert repeats >= 1
        assert all([self.repeat_blocks[i] is None for i in range(start, end)])

        for i in range(start, end):
            self.repeat_blocks[i] = (start, end, repeats)

    def compress(self):
        # Return a copy of this circuit with unnecessary idle time removed.
        # TODO - implement!
        raise NotImplementedError

    def add_idle_noise(self, idling_noise: OneQubitNoise | None):
        """Adds idling noise everywhere in the circuit

        Idling noise is added at every tick to qubits that have been initialized but on which no gate is performed

        Args:
            noise_model (OneQubitNoise | None): Noise channel to apply to idling locations in the circuit.
        """

        # Not a good idea to call this method before compression is done.
        if idling_noise is not None:
            instructions = sorted(self.instructions.items())
            # note that this only loop through ticks at which there is at least one instruction
            for tick, qubit_instructions in instructions:
                # Only interested in even ticks, where actual gates happen.
                if tick % 2 == 0:
                    # Find out which qubits were idle at this tick. These are those
                    # that are initialised but not involved in any gate.
                    initialised_qubits = {
                        qubit
                        for qubit in self.qubits
                        if self.is_initialised(tick, qubit)
                    }
                    active_qubits = set(qubit_instructions.keys())
                    idle_qubits = initialised_qubits.difference(active_qubits)
                    for qubit in idle_qubits:
                        noise = idling_noise.instruction([qubit])
                        self.add_instruction(tick + 1, noise)

    def to_stim(
        self,
        idling_noise: OneQubitNoise | None,
        track_coords: bool = True,
        track_progress: bool = True,
    ) -> stim.Circuit:
        """Transforms the circuit to a stim circuit.

        Args:
            idling_noise (OneQubitNoise | None): Noise channel to apply to idling locations in the circuit. Note that using to_stim will only add idling noise.
            track_coords (bool, optional): Whether to track the coordinates of the qubits and detectors. Defaults to True.
            track_progress (bool, optional): If this is set to True a progress bar is printed. The progress bar shows how many
                                             ticks have been translated and the time taken. Defaults to True.

        Returns:
            stim.Circuit: the resulting stim circuit.

        """
        if track_progress:
            # TODO - bug here: sometimes this progress bar overfills!
            with alive_bar(len(self.instructions), force_tty=True) as bar:
                return self._to_stim(idling_noise, track_coords, bar)
        else:
            return self._to_stim(idling_noise, track_coords, None)

    def _to_stim(
        self, idling_noise: OneQubitNoise | None, track_coords: bool, progress_bar: Any
    ) -> stim.Circuit:
        """Called by to_stim() to transform the circuit to a stim circuit.

        Args:
            idling_noise (OneQubitNoise | None): Noise channel to apply to idling locations in the circuit. Note that using to_stim will only add idling noise.
            track_coords (bool): Whether to track the coordinates of the qubits and detectors. Defaults to True.
            progress_bar (Any): None or an alive progress bar

        Returns:
            stim.Circuit: the resulting stim circuit.
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
        self.add_idle_noise(idling_noise)

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
            # further instructions - e.g. building detectors, adding checks
            # into logical observables, etc.
            further_instructions = self.measurer.measurements_to_stim(
                measurements, shift_coords
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
            instruction (Instruction): The instruction to be translated
            circuit (stim.Circuit): A stim circuit to add the instruction to.
        """
        if instruction.targets is not None:
            targets = instruction.targets
        else:
            targets = [self.qubit_index(qubit) for qubit in instruction.qubits]
        circuit.append(instruction.name, targets, instruction.params)

    def entered_repeat_block(self, tick: int, last_tick: int):
        # Return whether we've entered a repeat block between these two ticks.
        last_block = self.repeat_blocks[last_tick]
        this_block = self.repeat_blocks[tick]
        return last_block != this_block and this_block is not None

    def left_repeat_block(self, tick: int, last_tick: int):
        # Return whether we've left a repeat block between these two ticks -
        # if we have, return the number of times the block should be repeated
        last_block = self.repeat_blocks[last_tick]
        this_block = self.repeat_blocks[tick]
        if this_block != last_block and last_block is not None:
            start, end, repeats = last_block
            return repeats
        else:
            return None

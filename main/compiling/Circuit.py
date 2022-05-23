from collections import defaultdict
from typing import List, Dict, Tuple

import stim

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.compiling.Gate import Gate


RepeatBlock = Tuple[int, int, int] | None


class Circuit:
    def __init__(self):
        """ Intermediate representation of a quantum circuit. Rather than
        compile directly to a Stim circuit, which is somewhat inflexible, we
        first compile to our own Circuit class. One should picture a circuit
        diagram - that is, a 2D lattice, with gates placed on vertices. Time
        flows left to right, so each horizontal line represents a qubit.

        We consider noise to be a type of gate. All noise EXCEPT idling noise
        is included in the circuit diagram: idling noise is added in right
        before the Circuit is compiled further to an actual Stim circuit.

        At a given location (tick, qubit) in the circuit, only one genuine
        gate can occur. But multiple noise gates can exist at a single site -
        e.g. noise arising because a single qubit gate was just performed,
        plus noise arising because we're about to perform a measurement.
        """
        self.gates = defaultdict(lambda: defaultdict(list))
        self.stim_indexes = {}
        # Track at which ticks qubits were initialised and measured, so we
        # say whether a qubit is currently initialised or not.
        self.init_ticks = defaultdict(list)
        self.measure_ticks = defaultdict(list)

        # For each tick, note whether it's inside a repeat block.
        self.repeat_blocks: Dict[int, RepeatBlock] = defaultdict(lambda: None)

        # Track which measurements tell us the value of which checks
        self.checks_measured = {}

    def stim_index(self, qubit: Qubit):
        # Get the stim index corresponding to this qubit, or create one if
        # it doesn't yet have one.
        if qubit in self.stim_indexes:
            index = self.stim_indexes[qubit]
        else:
            index = len(self.stim_indexes)
            self.stim_indexes[qubit] = index
        return index

    def is_initialised(self, tick: int, qubit: Qubit):
        # At this tick, return whether this qubit has been initialised
        # but not yet measured
        inits = [t for t in sorted(self.init_ticks[qubit]) if t <= tick]
        measures = [t for t in sorted(self.measure_ticks[qubit]) if t <= tick]
        return max(inits, default=0) > max(measures, default=0)

    def initialise(self, tick: int, gates: List[Gate]):
        # Initialise a single qubit using the specified gates.
        qubits = {qubit for gate in gates for qubit in gate.qubits}
        # We only allow one qubit to be initialised at a time.
        assert len(qubits) == 1
        qubit = qubits.pop()

        # We want to know the tick at which we apply the last gate,
        # since this is when the qubit is considered 'initialised'
        initialised_tick = tick
        for i, gate in enumerate(gates):
            gate_tick = tick + 2*i
            self.add_gate(gate_tick, gate)
            initialised_tick = gate_tick
        # Note down at which tick this qubit is considered initialised.
        self.init_ticks[qubit].append(initialised_tick)

    def measure(self, tick: int, gate: Gate, check: Check, round: int):
        # Measure a qubit (perhaps multiple)
        self.add_gate(tick, gate)
        # Record that these qubits have been measured.
        for qubit in gate.qubits:
            self.measure_ticks[qubit].append(tick)
        # Note down that this gate corresponds to the measurement of a
        # particular check in a particular round. This info is used when
        # building detectors later.
        self.checks_measured[gate] = (check, round)

    def add_gate(self, tick: int, gate: Gate, is_noise=False):
        # Even ticks are for genuine gates, odd ticks are for noise.
        assert tick % 2 == (1 if is_noise else 0)
        assert gate.is_noise == is_noise
        for qubit in gate.qubits:
            gates = self.gates[tick][qubit]
            gates.append(gate)
            if len(gates) > 1:
                assert all([gate.is_noise for gate in gates])

    def add_noise(self, tick, noise_gate: Gate):
        self.add_gate(tick, noise_gate, is_noise=True)

    def add_repeat_block(self, start: int, end: int, repeats: int):
        # start inclusive, end exclusive.
        # Check this repeat block doesn't overlap with others, etc.
        assert start + 1 < end
        assert repeats >= 1
        assert all([
            self.repeat_blocks[i] is None
            for i in range(start, end)])

        for i in range(start, end):
            self.repeat_blocks[i] = (start, end, repeats)

    def compress(self):
        # Return a copy of this circuit with unnecessary idle time removed.
        raise NotImplementedError

    def to_stim(self):
        # Track which gates have been compiled to stim.
        compiled = defaultdict(bool)
        full_circuit = stim.Circuit()
        # Let 'circuit' denote the circuit we're currently compiling to - if
        # using repeat blocks, this need not always be the full circuit itself
        circuit = full_circuit
        # Track how many measurements have been made in total - this lets us
        # say how many measurements ago a specific measurement was, which is
        # vital for compiling detectors.
        measurements = 0
        last_tick = -1
        # TODO - add idle noise.
        for tick, qubit_gates in sorted(self.gates.items()):
            # Check whether we need to close a repeat block
            repeats = self.left_repeat_block(tick, last_tick)
            if repeats is not None:
                repeat_circuit = stim.CircuitRepeatBlock(repeats, circuit)
                full_circuit.append(repeat_circuit)
                circuit = full_circuit
            # Then check whether we need to start a new repeat block
            if self.entered_repeat_block(tick, last_tick):
                circuit = stim.Circuit()

            # Now actually compile gates
            for qubit, gates in qubit_gates.items():
                for gate in gates:
                    if not compiled[gate]:
                        self.gate_to_stim(gate, circuit, measurements)
                        measurements += (1 if gate.is_measurement else 0)
                        compiled[gate] = True
            circuit.append('TICK')
            last_tick = tick

        # If we've finished inside a repeat block, close it.
        repeat_block = self.repeat_blocks[last_tick]
        if repeat_block is not None:
            start, end, repeats = repeat_block
            repeat_circuit = stim.CircuitRepeatBlock(repeats, circuit)
            full_circuit.append(repeat_circuit)

        return full_circuit

    def gate_to_stim(self, gate: Gate, circuit: stim.Circuit, measurements: int):
        indexes = [self.stim_index(q) for q in gate.qubits]
        circuit.append(gate.name, indexes, gate.params)
        if gate.is_measurement:
            # Check whether we need to build a detector as a result of this
            # measurement
            check, round = self.checks_measured[gate]
            # Note what number this measurement is assigned by stim.
            check.measurements[round] = measurements
            for detector in check.detectors_triggered:
                # If this check (amongst others) triggers a detector,
                # note this down
                detector.triggers_measured.add(check)
                if detector.triggers_measured == detector.triggers:
                    # All triggers measured - can now compile this detector!
                    # (Or at the very least, its lid)
                    targets = detector.get_targets(round, measurements + 1)
                    targets = [stim.target_rec(t) for t in targets]
                    circuit.append('DETECTOR', targets)

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








from abc import abstractmethod, ABC
from typing import Iterable

from main.building_blocks.Check import Check
from main.compiling.Gate import Gate
from main.QPUs.QPU import QPU
from main.codes.Code import Code
from main.building_blocks.PauliLetter import PauliX, PauliZ, PauliY
from main.building_blocks.Qubit import Qubit
from main.building_blocks.Pauli import Pauli
from main.compiling.Circuit import Circuit
from main.compiling.noise.models.NoNoise import NoNoise
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.syndrome_extraction.extractors.SyndromeExtractor import SyndromeExtractor
from main.enums import State


class Compiler(ABC):
    def __init__(
            self, noise_model: NoiseModel | None,
            syndrome_extractor: SyndromeExtractor):
        if noise_model is None:
            noise_model = NoNoise()
        self.noise_model = noise_model
        self.syndrome_extractor = syndrome_extractor
        self.state_init_gates = {
            State.Zero: ['RZ'],
            State.One: ['RZ', 'X'],
            State.Plus: ['RX'],
            State.Minus: ['RX', 'Z'],
            State.I: ['RY'],
            State.MinusI: ['RY', 'X']}
        self.measurement_gates = {
            PauliX: 'MX',
            PauliY: 'MY',
            PauliZ: 'MZ'}

    def compile_qpu(self, qpu: QPU, circuit: Circuit, n_timesteps: int = 1):
        pass

    def compile_code(
            self, code: Code, layers: int, perfect_final_layer: bool = True,
            extract_checks_sequentially: bool = False, tick: int = 0,
            circuit: Circuit = None):
        assert layers > 0

        # Can compile onto an existing circuit (e.g. in a lattice surgery
        # or gauge fixing protocol), or start a new circuit from scratch.
        if circuit is None:
            assert tick == 0
            circuit = Circuit()

        # If this is the first time this code is being compiled, add ancilla
        # qubits (if needed)
        self.add_ancilla_qubits(code)

        new_data_qubits = [
            qubit for qubit in code.data_qubits.values()
            if not circuit.is_initialised(tick, qubit)]
        # Initialise data qubits, and set the 'current' tick to be the tick
        # we're on after all data qubits have been initialised.
        tick = self.initialize_qubits(new_data_qubits, tick, circuit)

        # First layer has to be done separately (i.e. can't be inside a
        # repeat block), because of how detectors differ in the first layer
        # compared to later layers. If there is only one layer, compile it
        # using the code for compiling the final layer below.
        layer = 0
        if layers > 1:
            tick = self.compile_layer(tick, layer, code, circuit)
            layer += 1

        # If perfect final layer is not needed, can compile the remaining
        # layers using a repeat block. If perfect final layer is needed,
        # can compile all but this final layer with a repeat block.
        if layers > 2 or (layers == 2 and not perfect_final_layer):
            repeats = layers - 1 - (1 if perfect_final_layer else 0)
            assert repeats >= 1
            layer_start = tick - 1  # inclusive...
            tick = self.compile_layer(tick, layer, code, circuit)
            layer_end = tick - 1  # ...exclusive
            circuit.add_repeat_block(layer_start, layer_end, repeats)
            layer += 1

        # Now just need to compile final layer, if it wasn't already included
        # in the repeat block above.
        if layers == 1 or perfect_final_layer:
            if not perfect_final_layer:
                tick = self.compile_layer(tick, layer, code, circuit)
            else:
                # Temporarily remove measurement noise for final layer...
                measurement_noise = self.noise_model.measurement
                self.noise_model.measurement = None
                tick = self.compile_layer(tick, layer, code, circuit)
                # ...now put measurement noise back as it was.
                self.noise_model.measurement = measurement_noise
            layer += 1

        # TODO - add observable

        return circuit.to_stim(self.noise_model)

    @abstractmethod
    def add_ancilla_qubits(self, code):
        # Implementation specific!
        pass

    def compile_layer(self, tick: int, layer: int, code: Code, circuit: Circuit):
        for i in range(code.schedule_length):
            round = (layer * code.schedule_length) + i
            # Compile one round of checks, and note down the final tick
            # used, then start the next round of checks from this tick.
            tick = self.compile_round(round, code, tick, circuit)
        return tick

    def add_start_of_round_noise(self, code: Code, tick: int, circuit: Circuit):
        noise = self.noise_model.data_qubit_start_round
        if noise is not None:
            for qubit in code.data_qubits.values():
                circuit.add_noise(tick, noise.gate([qubit]))

    def compile_round(
            self, round_number: int, code: Code, tick: int,
            circuit: Circuit):
        self.add_start_of_round_noise(code, tick - 1, circuit)
        # We will eventually return the tick we're on after one whole round
        # has been compiled.
        final_tick = tick

        # TODO - something like the following. The current design (only
        #  letting the syndrome extractor handle one check at a time)
        #  only works because ancilla measurement, initialisation and data
        #  qubit rotation right now always require exactly one gate, so
        #  everything stays in sync. When the user can pass in their
        #  own native gate set, this may not be true - e.g. reset in X
        #  basis may be done by resetting to Z then applying H.
        # round = code.schedule[round_number % code.schedule_length]
        # tick = self.syndrome_extractor.extract_round(
        #     tick, round, round_number, circuit, self)
        # return tick

        for check in code.schedule[round_number % code.schedule_length]:
            check_tick = self.syndrome_extractor.extract_check(
                tick, check, circuit, self, round_number)

            if not self.syndrome_extractor.extract_checks_in_parallel:
                # If extracting one check at a time, need to increase the
                # 'main' tick variable, so that checks aren't compiled in
                # parallel.
                tick = check_tick
            final_tick = max(final_tick, check_tick)

        return final_tick

    def measure_qubit(self, qubit: Qubit, tick: int, basis: Pauli, circuit: Circuit, check: Check, round: int):
        # TODO - generalise for native multi-qubit measurements.
        noise = self.noise_model.measurement
        params = noise.params if noise is not None else ()
        gate_name = self.measurement_gates[basis]
        measurement_gate = Gate([qubit], gate_name, params, is_measurement=True)
        circuit.measure(tick, measurement_gate, check, round)
        return tick + 2

    def initialize_qubits(self, qubits: Iterable[Qubit], tick: int, circuit: Circuit):
        # TODO - user passes in own native gate set.
        # Note down how many ticks were needed - we will return the tick we're on
        # after the initialisation is complete.
        ticks_needed = 0
        noise = self.noise_model.initialisation

        for qubit in qubits:
            # Figure out which gates are needed to initialise in the given state
            init_gates = [
                Gate([qubit], gate_name)
                for gate_name in self.state_init_gates[qubit.initial_state]]
            circuit.initialise(tick, init_gates)
            gates_needed = len(init_gates)
            # Add noise, if needed.
            if noise is not None:
                for i in range(len(init_gates)):
                    noise_tick = tick + (2 * gates_needed - 1)
                    circuit.add_noise(noise_tick, noise.gate([qubit]))

            ticks_needed = max(ticks_needed, 2 * gates_needed)

        return tick + ticks_needed

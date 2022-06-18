from abc import abstractmethod, ABC
from typing import Iterable, List

from main.building_blocks.Check import Check
from main.building_blocks.Detector import Detector
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.compiling.Instruction import Instruction
from main.QPUs.QPU import QPU
from main.codes.Code import Code
from main.building_blocks.pauli.PauliLetter import PauliX, PauliZ, PauliY
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli.Pauli import Pauli
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
        self.state_init_instructions = {
            State.Zero: ['RZ'],
            State.One: ['RZ', 'X'],
            State.Plus: ['RX'],
            State.Minus: ['RX', 'Z'],
            State.I: ['RY'],
            State.MinusI: ['RY', 'X']}
        self.basis_measurements = {
            PauliX: 'MX',
            PauliY: 'MY',
            PauliZ: 'MZ'}

    def compile_qpu(
            self, qpu: QPU, layers: int, tick: int = 0,
            circuit: Circuit = None):
        pass

    def compile_code(
            self, code: Code, layers: int, tick: int = 0,
            circuit: Circuit = None):
        assert layers > 0

        circuit, tick = self.compile_initialisation(code, circuit, tick)

        # Can compile the remaining layers using a repeat block.
        if layers > 1:
            layer_start = tick - 1  # inclusive...
            tick = self.compile_layer(tick, 1, code, circuit)
            layer_end = tick - 1  # ...exclusive
            repeats = layers - 1
            circuit.add_repeat_block(layer_start, layer_end, repeats)

        # TODO - implement these too!
        # self.compile_final_detectors()
        # self.compile_logical_operator()

        return circuit.to_stim(self.noise_model)

    def compile_initialisation(self, code: Code, circuit: Circuit, tick: int):
        # TODO - no idea yet how to glue together detectors of different codes
        #  - e.g. in a lattice surgery protocol, when we have separate codes,
        #  then a merged code, then separate codes again.
        # TODO - this method should take in an 'initial_logical_states'
        #  parameter, which is a dictionary whose keys are logical qubits and
        #  values are states. This should then be used to determine which
        #  states to initialise the *individual* data qubits to. (Currently
        #  the initial data qubit states are defined when the code is defined,
        #  but this seems logically wrong).
        # TODO - definition of code can perhaps flag in some way which checks
        #  will be deterministic in the first round when initialised in a
        #  particular logical state. Then we have a way of building only
        #  deterministic detectors in round one (in later rounds they should
        #  all be deterministic).

        # Can compile onto an existing circuit (e.g. in a lattice surgery
        # or gauge fixing protocol), or start a new circuit from scratch.
        if circuit is None:
            assert tick == 0
            circuit = Circuit()
        circuit.measurer.add_detectors(code.detectors)

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
        # compared to later layers.
        tick = self.compile_layer(tick, 0, code, circuit)

        return circuit, tick

    def compile_final_detectors(
            self, detectors: List[Detector], perfect_lids: bool = True):
        # For ending a simulation. We need to measure a logical observable,
        # but we also need to catch errors since the last round of check
        # measurements that could flip this logical. So we're going to need
        # some more detectors. The lids of these detectors should together
        # contain measurements that can be used to deduce a logical operator.
        # The floors of the detectors should be checks that have already
        # been measured as part of the usual code schedule.
        pass

    def compile_logical_operator(self, logical: LogicalOperator):
        # After final detectors have been compiled, a subset of the checks
        # used in the lids of these detectors should be used to get the
        # logical measurement outcome.
        pass

    @abstractmethod
    def add_ancilla_qubits(self, code):
        # Implementation specific!
        pass

    def compile_layer(
            self, tick: int, layer: int, code: Code, circuit: Circuit):
        for relative_round in range(code.schedule_length):
            # Compile one round of checks, and note down the final tick
            # used, then start the next round of checks from this tick.
            round = (layer * code.schedule_length) + relative_round
            tick = self.compile_round(
                round, relative_round, code, tick, circuit)
        return tick

    def add_start_of_round_noise(self, code: Code, tick: int, circuit: Circuit):
        noise = self.noise_model.data_qubit_start_round
        if noise is not None:
            for qubit in code.data_qubits.values():
                circuit.add_instruction(tick, noise.instruction([qubit]))

    def compile_round(
            self, round: int, relative_round: int, code: Code, tick: int,
            circuit: Circuit):
        self.add_start_of_round_noise(code, tick - 1, circuit)
        # We will eventually return the tick we're on after one whole round
        # has been compiled.
        final_tick = tick

        # TODO - The current design (only
        #  letting the syndrome extractor handle one check at a time)
        #  only works because ancilla measurement, initialisation and data
        #  qubit rotation right now always require exactly one gate, so
        #  everything stays in sync. When the user can pass in their
        #  own native gate set, this may not be true - e.g. reset in X
        #  basis may be done by resetting to Z then applying H. So in future
        #  need to pass to the syndrome extractor the max number of native
        #  gates a desired gate implementation can take, so that all ops
        #  across the round can be kept in sync. De-idler will remove
        #  unnecessary idle noise later.

        for check in code.schedule[relative_round]:
            check_tick = self.syndrome_extractor.extract_check(
                tick, check, circuit, self, round, relative_round)

            if not self.syndrome_extractor.extract_checks_in_parallel:
                # If extracting one check at a time, need to increase the
                # 'main' tick variable, so that checks aren't compiled in
                # parallel.
                tick = check_tick
            final_tick = max(final_tick, check_tick)

        return final_tick

    def measure_qubit(
            self, qubit: Qubit, tick: int, basis: Pauli, circuit: Circuit,
            check: Check, round: int, relative_round: int):
        # TODO - generalise for native multi-qubit measurements.
        noise = self.noise_model.measurement
        params = noise.params if noise is not None else ()
        measurement_name = self.basis_measurements[basis]
        measurement = Instruction(
            [qubit], measurement_name, params, is_measurement=True)
        circuit.measure(tick, measurement, check, round, relative_round)
        return tick + 2

    def initialize_qubits(self, qubits: Iterable[Qubit], tick: int, circuit: Circuit):
        # TODO - user passes in own native gate set.
        # Note down how many ticks were needed - we will return the tick
        # we're on after the initialisation is complete.
        ticks_needed = 0
        noise = self.noise_model.initialisation

        for qubit in qubits:
            # Figure out which instructions are needed to initialise in the
            # given state
            init_instructions = [
                Instruction([qubit], name)
                for name in self.state_init_instructions[qubit.initial_state]]
            circuit.initialise(tick, init_instructions)
            instructions_needed = len(init_instructions)
            # Add noise, if needed.
            if noise is not None:
                for i in range(len(init_instructions)):
                    noise_tick = tick + (2 * instructions_needed - 1)
                    circuit.add_instruction(
                        noise_tick, noise.instruction([qubit]))

            ticks_needed = max(ticks_needed, 2 * instructions_needed)

        return tick + ticks_needed

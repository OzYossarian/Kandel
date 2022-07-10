from abc import abstractmethod, ABC
from typing import Iterable, List, Dict, Tuple

from main.building_blocks.Check import Check
from main.building_blocks.Detector import Detector
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.building_blocks.pauli.utils import stabilizers
from main.compiling.Instruction import Instruction
from main.QPUs.QPU import QPU
from main.codes.Code import Code
from main.building_blocks.pauli.PauliLetter import PauliX, PauliZ, PauliY, PauliLetter
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli.Pauli import Pauli
from main.compiling.Circuit import Circuit
from main.compiling.noise.models.NoNoise import NoNoise
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.syndrome_extraction.extractors.SyndromeExtractor import SyndromeExtractor
from main.enums import State
from main.stabilizer_formalism.StabilizerGroup import StabilizerGroup


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
            self, code: Code, layers: int,
            initial_states: Dict[Qubit, State],
            final_measurements: List[Pauli],
            logical_observables: List[LogicalOperator]):
        # TODO - yet to settle on a good way of designing how the user ends
        #  a memory experiment. We need to accomplish two things:
        #  1. Measure a logical observable (maybe multiple if we have
        #     multiple qubits)
        #  2. Add detectors capable of detecting errors that occur between
        #     the final measurement round and the logical observable measurement.
        #  Some thoughts:
        #    Knowing what the logical observable is (i.e. as a Pauli product)
        #  at any given time is part of the code definition - completely
        #  compiler independent. But how to measure it can be compiler
        #  specific - e.g. perhaps one compiler only has native two qubit
        #  measurements, while another can only do single qubit measurements.
        #  This differs from initialisation - there, regardless of compiler,
        #  a particular initial logical state just corresponds to some
        #  particular initial data qubit states (though perhaps this is
        #  itself a simplifying assumption - maybe in reality there are
        #  architectures that can only initialise immediately into bell pairs
        #  or something??)
        #    For now, make simplifying assumption that all final measurements
        #  are single qubit data measurements.
        assert layers > 0
        initial_detector_schedule, tick, circuit = self.compile_initialisation(
            code, initial_states)
        tick = self.compile_layer(
            0, initial_detector_schedule, logical_observables,
            tick, circuit, code)

        # Can compile the remaining layers using a repeat block.
        # TODO - No we can't! For codes whose logical observables are static,
        #  or at least repeat periodically, we can. But this isn't generally
        #  true for a floquet/dynamic code. So can we find a nice way of
        #  detecting whether or not we can add a repeat block? Or rather,
        #  a way of making the final Stim circuit more human readable - e.g.
        #  by implementing a way of adding comments to the circuit?
        layer = 1
        while layer < layers:
            tick = self.compile_layer(
                layer, code.detector_schedule, logical_observables,
                tick, circuit, code)
            layer += 1

        self.compile_final_measurements(
            final_measurements, logical_observables, layer, tick,
            circuit, code)

        return circuit.to_stim(self.noise_model)

    def compile_initialisation(
            self, code: Code, initial_states: Dict[Qubit, State]):
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

        # For now, always start a new circuit from scratch. Later, allow
        # compilation onto an existing circuit (e.g. in a lattice surgery or
        # gauge fixing protocol),
        circuit = Circuit()
        tick = 0

        # Add ancilla qubits (if needed)
        self.add_ancilla_qubits(code)

        # Initialise data qubits, and set the 'current' tick to be the tick
        # we're on after all data qubits have been initialised.
        tick = self.initialize_qubits(initial_states, tick, circuit)

        # In the first ever round, must remove non-deterministic detectors
        initial_detector_schedule = self.deterministic_initial_detectors(
            initial_states, code)

        return initial_detector_schedule, tick, circuit

    def deterministic_initial_detectors(
            self, initial_states: Dict[Qubit, State], code: Code):
        # Initialise the stabilizer group to be tracked. We will be checking
        # whether the Pauli product learned by each detector commutes with
        # everything in the stabilizer group.
        generators = [
            PauliProduct([Pauli(qubit, stabilizers[state])])
            for qubit, state in initial_states.items()]
        stabilizer_group = StabilizerGroup(generators)

        initial_detector_schedule = [[] for _ in range(code.schedule_length)]
        for round in range(code.schedule_length):
            for detector in code.detector_schedule[round]:
                assert detector.lid_end == round
                if detector.floor_start < round <= detector.lid_start:
                    # This detector should become a 'lid-only' detector in
                    # the first round, unless it's non-deterministic.
                    if stabilizer_group.commutes(detector.stabilizer):
                        initial_detector_schedule[round].append(detector)
                else:
                    # This detector is always going to be comparing a floor
                    # with a lid, so should always be deterministic.
                    initial_detector_schedule[round].append(detector)
            # Now add the checks from this round into the stabilizer group and
            # repeat the process.
            stabilizer_group.measure([
                PauliProduct(check.paulis)
                for check in code.check_schedule[round]])
        return initial_detector_schedule

    @abstractmethod
    def add_ancilla_qubits(self, code):
        # Implementation specific!
        pass

    def initialize_qubits(
            self, initial_states: Dict[Qubit, State],
            tick: int, circuit: Circuit):
        # TODO - user passes in own native gate set.
        # Note down how many ticks were needed - we will return the tick
        # we're on after the initialisation is complete.
        ticks_needed = 0
        noise = self.noise_model.initialisation

        for qubit, state in initial_states.items():
            # Figure out which instructions are needed to initialise in the
            # given state
            init_instructions = [
                Instruction([qubit], name)
                for name in self.state_init_instructions[state]]
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

    def compile_layer(
            self, layer: int, detector_schedule: List[List[Detector]],
            observables: List[LogicalOperator], tick: int, circuit: Circuit,
            code: Code):
        for relative_round in range(code.schedule_length):
            # Compile one round of checks, and note down the final tick
            # used, then start the next round of checks from this tick.
            round = layer * code.schedule_length + relative_round
            tick = self.compile_round(
                round, relative_round, detector_schedule, observables,
                tick, circuit, code)
        return tick

    def compile_round(
            self, round: int, relative_round: int,
            detector_schedule: List[List[Detector]],
            observables: List[LogicalOperator], tick: int, circuit: Circuit,
            code: Code):
        self.add_start_of_round_noise(tick - 1, circuit, code)
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

        # First compile the syndrome extraction circuits for the checks.
        for check in code.check_schedule[relative_round]:
            check_tick = self.syndrome_extractor.extract_check(
                check, round, self, tick, circuit)

            if not self.syndrome_extractor.extract_checks_in_parallel:
                # If extracting one check at a time, need to increase the
                # 'main' tick variable, so that checks aren't compiled in
                # parallel.
                tick = check_tick
            final_tick = max(final_tick, check_tick)

        # Next note down any detectors we'll need to build at this round.
        detectors = detector_schedule[relative_round]
        circuit.measurer.add_detectors(detectors, round)

        # And likewise note down any logical observables that need updating.
        observable_updates = code.update_logical_qubits(round)
        for observable in observables:
            circuit.measurer.add_to_logical_observable(
                observable_updates[observable], observable, round)

        return final_tick

    def add_start_of_round_noise(
            self, tick: int, circuit: Circuit, code: Code):
        noise = self.noise_model.data_qubit_start_round
        if noise is not None:
            for qubit in code.data_qubits.values():
                circuit.add_instruction(tick, noise.instruction([qubit]))

    def compile_final_measurements(
            self, final_measurements: List[Pauli],
            logical_observables: List[LogicalOperator], layer: int, tick: int,
            circuit: Circuit, code: Code):
        # We consider this the start of a new round, so add corresponding
        # noise if needed.
        self.add_start_of_round_noise(tick - 1, circuit, code)

        # A single qubit measurement is just a weight-1 check, and writing
        # them as checks rather than Paulis fits them into the same framework
        # as other measurements.
        final_checks = {
            pauli.qubit: Check([pauli]) for pauli in final_measurements}

        # First, compile instructions for actually measuring the qubits.
        round = layer * code.schedule_length
        for pauli in final_measurements:
            self.measure_qubit(
                pauli.qubit, pauli.letter, final_checks[pauli.qubit], round,
                tick, circuit)

        # Now try to use these as lids for any detectors that at this point
        # have a floor but no lid.
        self.compile_final_detectors(final_checks, round, circuit, code)

        # Finally, define the logical observables we want to measure
        self.compile_initial_logical_observables(
            logical_observables, final_checks, round, circuit)

    def compile_final_detectors(
            self, final_checks: Dict[Qubit, Check], round: int,
            circuit: Circuit, code: Code):
        final_detectors = []
        for detector in code.detectors:
            if detector.is_open(relative_round=-1):
                # This detector can potentially be 'finished off', if our
                # final data qubit measurements are in the right bases.
                detector_qubits = {
                    pauli.qubit for pauli in detector.stabilizer.paulis}
                measurements = [
                    final_checks[data_qubit].paulis[0]
                    for data_qubit in detector_qubits]
                # TODO - shouldn't need to sort. Should just compare products
                #  themselves, not words.
                measurement_product = PauliProduct(measurements)
                if detector.stabilizer.word == measurement_product.word:
                    # Can make a lid for this detector!
                    floor = [
                        (t + detector.lid_end, check)
                        for t, check in detector.floor]
                    lid = [
                        (0, final_checks[qubit])
                        for qubit in detector_qubits]
                    final_detectors.append(Detector(floor, lid, 0))

        # Finally, compile these detectors to the circuit.
        circuit.measurer.add_detectors(final_detectors, round)

    def compile_initial_logical_observables(
            self, logical_observables: List[LogicalOperator],
            final_checks: Dict[Qubit, Check], round: int, circuit: Circuit):
        # The Paulis that initially made up the logical observables that we
        # want to measure should be a subset of the final individual data
        # qubit measurements.
        for observable in logical_observables:
            logical_checks = []
            for pauli in observable.initial_paulis:
                # Just double check that what we measured is actually what we
                # want to use to form the logical observable.
                check = final_checks[pauli.qubit]
                assert check.paulis[0].letter == pauli.letter
                logical_checks.append(check)
            # Compile to the circuit.
            circuit.measurer.add_to_logical_observable(
                logical_checks, observable, round)

    def measure_qubit(
            self, qubit: Qubit, basis: PauliLetter, check: Check, round: int,
            tick: int, circuit: Circuit):
        # TODO - generalise for native multi-qubit measurements.
        noise = self.noise_model.measurement
        params = noise.params if noise is not None else ()
        measurement_name = self.basis_measurements[basis]
        measurement = Instruction(
            [qubit], measurement_name, params, is_measurement=True)
        circuit.measure(measurement, check, round, tick)
        return tick + 2

from abc import abstractmethod, ABC
from typing import List, Dict, Iterable
from main.building_blocks.Check import Check
from main.building_blocks.detectors.Detector import Detector
from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.building_blocks.pauli.utils import plus_one_eigenstates
from main.compiling.Instruction import Instruction
from main.codes.Code import Code
from main.building_blocks.pauli.PauliLetter import PauliX, PauliZ, PauliY, PauliLetter
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli.Pauli import Pauli
from main.compiling.Circuit import Circuit
from main.compiling.compilers.Determiner import Determiner
from main.compiling.noise.models.NoNoise import NoNoise
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.noise.noises.Noise import Noise
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import (
    TrivialOrderer,
)
from main.compiling.syndrome_extraction.extractors.SyndromeExtractor import (
    SyndromeExtractor,
)
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CnotExtractor import (
    CnotExtractor,
)
from main.utils.enums import State
from main.utils.types import Tick
from main.utils.utils import xor
import stim


class Compiler(ABC):
    def __init__(
        self,
        noise_model: NoiseModel = None,
        syndrome_extractor: SyndromeExtractor = None,
        initialisation_instructions: Dict[State, List[str]] = None,
        measurement_instructions: Dict[PauliLetter, List[str]] = None,
    ):
        # Configure defaults
        if noise_model is None:
            noise_model = NoNoise()
        if syndrome_extractor is None:
            # Fall back to some general syndrome extractor. But note that
            # without providing an ordering, this might try to place two
            # controlled gates on the same qubit at once, which will raise
            # an error.
            syndrome_extractor = CnotExtractor(TrivialOrderer())
        if initialisation_instructions is None:
            initialisation_instructions = {
                State.Zero: ["RZ"],
                State.One: ["RZ", "X"],
                State.Plus: ["RX"],
                State.Minus: ["RX", "Z"],
                State.I: ["RY"],
                State.MinusI: ["RY", "X"],
            }
        if measurement_instructions is None:
            measurement_instructions = {PauliX: ["MX"], PauliY: ["MY"], PauliZ: ["MZ"]}

        # All initialisations must start with a reset, but can follow it with
        # other types of gates
        assert all(
            instructions[0][0] == "R"
            for instructions in initialisation_instructions.values()
        )

        # Similarly, all measurements must end with an actual measurement, but
        # can be preceded by some other gates
        assert all(
            instructions[-1][0] == "M"
            for instructions in measurement_instructions.values()
        )

        self.noise_model = noise_model
        self.syndrome_extractor = syndrome_extractor
        self.initialisation_instructions = initialisation_instructions
        self.measurement_instructions = measurement_instructions

    def compile_code(
        self,
        code: Code,
        layers: int,
        initial_states: Dict[Qubit, State] = None,
        initial_stabilizers: List[Stabilizer] = None,
        final_measurements: List[Pauli] = None,
        final_stabilizers: List[Stabilizer] = None,
        logical_observables: List[LogicalOperator] = None,
    ) -> stim.Circuit():

        # TODO - actually might make more sense to only allow
        #  initial_stabilizers and final_stabilizers?? Is more general! But no
        #  harm keeping both for now.
        if not xor(initial_states is None, initial_stabilizers is None):
            raise ValueError(
                "Exactly one of initial_states and initial_stabilizers "
                "should be provided."
            )
        if final_measurements is not None and final_stabilizers is not None:
            raise ValueError(
                "Shouldn't provide both final_measurements and "
                "final_stabilizers - pick one!"
            )

        initial_detector_schedules, tick, circuit = self.compile_initialisation(
            code, initial_states, initial_stabilizers)

        initial_layers = len(initial_detector_schedules)
        # initial_layers is the number of layers in which 'lid-only'
        # detectors exist.
        if initial_layers > layers:
            raise ValueError(
                f"Requested that {layers} layer(s) are compiled, but code "
                f"seems to take {initial_layers} layer(s) to set up! Please "
                f"increase number of layers to compile"
            )

        # Compile these initial layers.
        for layer, detector_schedule in enumerate(initial_detector_schedules):
            tick = self.compile_layer(
                layer, detector_schedule, logical_observables, tick, circuit, code
            )

        # Compile the remaining layers.
        layer = initial_layers
        while layer < layers:
            tick = self.compile_layer(
                layer, code.detector_schedule, logical_observables, tick, circuit, code
            )
            layer += 1

        # Finish with data qubit measurements, and use these to reconstruct
        # some detectors.
        self.compile_final_measurements(
            final_measurements,
            final_stabilizers,
            logical_observables,
            layer,
            tick,
            circuit,
            code)

        return circuit.to_stim(self.noise_model.idling)

    def compile_initialisation(
        self,
        code: Code,
        initial_states: Dict[Qubit, State],
        initial_stabilizers: List[Stabilizer],
    ):
        # For now, always start a new circuit from scratch. Later, allow
        # compilation onto an existing circuit (e.g. in a lattice surgery or
        # gauge fixing protocol),
        circuit = Circuit()
        tick = 0
        self.add_ancilla_qubits(code)

        # Figure out states in which to initialise data qubits in order to
        # satisfy desired initial stabilizers.
        if initial_stabilizers is not None:
            initial_states = self.get_initial_states(initial_stabilizers)

        if len(initial_states) != len(code.data_qubits):
            raise ValueError(
                "Some data qubits' initial states either aren't given or "
                "aren't determined by the given initial stabilizers! Please "
                "give a complete set of desired initial states or desired "
                "stabilizers for the first round of measurements."
            )

        # Initialise data qubits, and set the 'current' tick to be the tick
        # we're on after all data qubits have been initialised.
        tick = self.initialize_qubits(initial_states, tick, circuit)

        # In the first few rounds (or even layers), there might be some
        # non-deterministic detectors that need removing.

        determiner = Determiner(code, self)
        initial_detector_schedules = determiner.get_initial_detectors(
            initial_states, initial_stabilizers
        )

        return initial_detector_schedules, tick, circuit

    @abstractmethod
    def add_ancilla_qubits(self, code):
        # Implementation specific!
        pass

    def get_measurement_bases(self, final_stabilizers: List[Stabilizer]):
        measurement_bases = list(self._get_paulis(final_stabilizers).values())
        return measurement_bases

    def get_initial_states(self, initial_stabilizers: List[Stabilizer]):
        paulis = self._get_paulis(initial_stabilizers)
        initial_states = {
            qubit: plus_one_eigenstates[pauli.letter] for qubit, pauli in paulis.items()
        }
        return initial_states

    def _get_paulis(self, stabilizers: List[Stabilizer]):
        paulis = {}
        for stabilizer in stabilizers:
            # TODO - does any extra work need to be done if it's -1? SURELY
            #  yes - e.g. if using these Paulis as measurement bases, means
            #  we need to flip a sign, yes? Could all get quite tricky if
            #  some stabilizers are +1 and some are -1...
            assert stabilizer.product.word.sign in [-1, 1]
            for pauli in stabilizer.product.paulis:
                # Can just use the plus one eigenstate of the Pauli, ignoring sign.
                pauli.letter.sign = 1
                existing = paulis.get(pauli.qubit, None)
                if existing is None:
                    paulis[pauli.qubit] = pauli
                elif existing != pauli:
                    raise ValueError(
                        f"The desired initial stabilizers are inconsistent! "
                        f"Qubit at {pauli.qubit.coords} resolves to "
                        f"both {existing.letter} and {pauli.letter}."
                    )
        return paulis

    def initialize_qubits(
        self,
        initial_states: Dict[Qubit, State],
        tick: int,
        circuit: Circuit,
        initialisation_instructions: Dict[State, List[str]] = None,
    ):
        # This method can also be used by a syndrome extractor, which might
        # have its own initialisation instructions.
        if initialisation_instructions is None:
            initialisation_instructions = self.initialisation_instructions

        # Note down how many ticks were needed - we will return the tick
        # we're on after the initialisation is complete.
        ticks_needed = 0
        noise = self.noise_model.initialisation

        for qubit, state in initial_states.items():
            # Get the instructions needed to initialise in the given state
            init_instructions = [
                Instruction([qubit], name)
                for name in initialisation_instructions[state]
            ]
            # Initialise with a reset gate and add noise if needed
            circuit.initialise(tick, init_instructions[0])
            if noise is not None:
                noise_instruction = noise.instruction([qubit])
                circuit.add_instruction(tick + 1, noise_instruction)
            # Now apply the remaining gates, again adding noise if needed
            remainder = init_instructions[1:]
            self.compile_one_qubit_gates(remainder, tick + 2, circuit)
            ticks_needed = max(ticks_needed, 2 * len(init_instructions))

        return tick + ticks_needed

    def compile_layer(
            self,
            layer: int,
            detector_schedule: List[List[Detector]],
            observables: List[LogicalOperator] | None,
            tick: int,
            circuit: Circuit,
            code: Code
    ) -> int:
        for relative_round in range(code.schedule_length):
            # Compile one round of checks, and note down the final tick
            # used, then start the next round of checks from this tick.
            round = layer * code.schedule_length + relative_round
            tick = self.compile_round(
                round,
                relative_round,
                detector_schedule,
                observables,
                tick,
                circuit,
                code,
            )
        return tick

    def compile_round(
        self,
        round: int,
        relative_round: int,
        detector_schedule: List[List[Detector]],
        observables: List[LogicalOperator] | None,
        tick: int,
        circuit: Circuit,
        code: Code,
    ):
        
        self.add_start_of_round_noise(tick - 1, circuit, code)

        # First compile the syndrome extraction circuits for the checks.
        checks = code.check_schedule[relative_round]
        tick = self.syndrome_extractor.extract_checks(
            checks, round, tick, circuit, self
        )

        # Next note down any detectors we'll need to build at this round.
        detectors = detector_schedule[relative_round]
        circuit.measurer.add_detectors(detectors, round)

        # And likewise note down any logical observables that need updating.
        if observables is not None:
            for observable in observables:
                checks_to_multiply_in = observable.update(round)
                circuit.measurer.multiply_logical_observable(
                    checks_to_multiply_in, observable, round)

        circuit.end_round(tick - 2)

        return tick

    def add_start_of_round_noise(self, tick: int, circuit: Circuit, code: Code):
        noise = self.noise_model.data_qubit_start_round
        if noise is not None:
            for qubit in code.data_qubits.values():
                circuit.add_instruction(tick, noise.instruction([qubit]))

    def compile_final_measurements(
        self,
        final_measurements: List[Pauli] | None,
        final_stabilizers: List[Stabilizer] | None,
        logical_observables: List[LogicalOperator] | None,
        layer: int,
        tick: int,
        circuit: Circuit,
        code: Code,
    ):
        # TODO - allow measurements other than single data qubits
        #  measurements at the end? e.g. Pauli product measurements.
        round = layer * code.schedule_length
        if final_stabilizers is not None:
            final_measurements = self.get_measurement_bases(final_stabilizers)

        # A single qubit measurement is just a weight-1 check, and writing
        # them as checks rather than Paulis fits them into the same framework
        # as other measurements.
        if final_measurements is not None:
            final_checks = {}
            for pauli in final_measurements:
                check = Check([pauli], pauli.qubit.coords)
                final_checks[pauli.qubit] = check

            # First, compile instructions for actually measuring the qubits.
            self.measure_qubits(
                final_measurements, final_checks.values(), round, tick, circuit
            )

            # Now try to use these as lids for any detectors that at this point
            # have a floor but no lid.
            self.compile_final_detectors(
                final_checks, final_stabilizers, layer, circuit, code
            )

            # Finally, define the logical observables we want to measure
            self.compile_initial_logical_observables(
                logical_observables, final_checks, round, circuit
            )

        elif logical_observables is not None:
            raise ValueError(
                "Can't measure any logical observables if no method is given "
                "for performing final measurements! Please provide one of "
                "final_measurements or final_stabilizers."
            )

    def compile_final_detectors(
        self,
        final_checks: Dict[Qubit, Check],
        final_stabilizers: List[Stabilizer],
        layer: int,
        circuit: Circuit,
        code: Code,
    ):
        round = layer * code.schedule_length
        if final_stabilizers is None:
            final_detectors = self.compile_final_detectors_from_measurements(
                final_checks, round, code
            )
        else:
            final_detectors = self.compile_final_detectors_from_stabilizers(
                final_checks, final_stabilizers
            )

        # Finally, add these detectors to the circuit.
        circuit.measurer.add_detectors(final_detectors, round)

    def compile_final_detectors_from_stabilizers(
        self, final_checks: Dict[Qubit, Check], final_stabilizers: List[Stabilizer]
    ):
        final_detectors = []
        for stabilizer in final_stabilizers:
            qubits = [pauli.qubit for pauli in stabilizer.product.paulis]
            measurements = [(0, final_checks[qubit]) for qubit in qubits]
            # TODO - some sanity checks here perhaps, that the checks in the
            #  drum's floor actually exist, etc.
            floor = stabilizer.timed_checks
            drum = Drum(floor, measurements, 0, stabilizer.anchor)
            final_detectors.append(drum)
        return final_detectors

    def compile_final_detectors_from_measurements(
            self, final_checks: Dict[Qubit, Check], round: int, code: Code):
        final_detectors = []
        for detector in code.detectors:
            open_lid, checks_measured = detector.has_open_lid(
                round - 1, code.schedule_length)
            if open_lid:
                # This detector can potentially be 'finished off', if our
                # final data qubit measurements are in the right bases
                detector_checks = sorted(
                    checks_measured, key=lambda timed_check: -timed_check[0])
                detector_product = PauliProduct(
                    [
                        pauli
                        for _, check in detector_checks
                        for pauli in check.paulis.values()
                    ]
                )
                detector_qubits = {pauli.qubit for pauli in detector_product.paulis}
                measurements = [
                    list(final_checks[data_qubit].paulis.values())[0]
                    for data_qubit in detector_qubits
                ]
                measurement_product = PauliProduct(measurements)

                if detector_product.equal_up_to_sign(measurement_product):
                    # Can make a lid for this detector!
                    floor = [
                        (t + detector.lid_end, check) for t, check in detector_checks
                    ]
                    lid = [(0, final_checks[qubit]) for qubit in detector_qubits]
                    final_detectors.append(Drum(floor, lid, 0, detector.anchor))

        return final_detectors

    def compile_initial_logical_observables(
        self,
        logical_observables: List[LogicalOperator] | None,
        final_checks: Dict[Qubit, Check] | None,
        round: int,
        circuit: Circuit,
    ):
        # The Paulis that initially made up the logical observables that we
        # want to measure should be a subset of the final individual data
        # qubit measurements.
        if logical_observables is not None:
            for observable in logical_observables:
                logical_checks = []
                for pauli in observable.at_round(-1):
                    # Just double check that what we measured is actually what we
                    # want to use to form the logical observable.
                    check = final_checks[pauli.qubit]
                    assert list(check.paulis.values())[0].letter == pauli.letter
                    logical_checks.append(check)
                # Compile to the circuit.
                circuit.measurer.multiply_logical_observable(
                    logical_checks, observable, round
                )

    # TODO - generalise for native multi-qubit measurements.
    def measure_qubits(
        self,
        paulis: Iterable[Pauli],
        checks: Iterable[Check],
        round: int,
        tick: int,
        circuit: Circuit,
        measurement_instructions: Dict[PauliLetter, List[str]] = None,
    ):
        # This method can also be used by a syndrome extractor, which might
        # have its own measurement instructions.
        if measurement_instructions is None:
            measurement_instructions = self.measurement_instructions
        measurement_noise = self.noise_model.measurement

        ticks_needed = 0
        for pauli, check in zip(paulis, checks):
            # `check` should correspond to the check whose outcome is given
            # by measuring the given single qubit Pauli, e.g. when a check is
            # measured using an ancilla.
            instructions = [
                Instruction([pauli.qubit], name)
                for name in measurement_instructions[pauli.letter]
            ]
            gates = instructions[:-1]
            # Compile gates needed before the measurement
            measurement_tick = self.compile_one_qubit_gates(gates, tick, circuit)
            # Now do the actual measurement.
            measurement = instructions[-1]
            measurement.is_measurement = True
            measurement.params = (
                measurement_noise.params if measurement_noise is not None else ()
            )
            circuit.measure(measurement, check, round, measurement_tick)

            ticks_needed = max(ticks_needed, 2 * len(instructions))

        return tick + ticks_needed

    def compile_one_qubit_gates(
        self, gates: List[Instruction], tick: int, circuit: Circuit
    ) -> Tick:
        return self._compile_gates(
            gates, self.noise_model.one_qubit_gate, 1, tick, circuit
        )

    def compile_two_qubit_gates(
        self, gates: List[Instruction], tick: int, circuit: Circuit
    ) -> Tick:
        return self._compile_gates(
            gates, self.noise_model.two_qubit_gate, 2, tick, circuit
        )

    def _compile_gates(
        self,
        gates: List[Instruction],
        noise: Noise,
        gate_size: int,
        tick: int,
        circuit: Circuit,
    ) -> Tick:
        """For compiling a list of gates IN SEQUENCE. i.e. Even if the gates
        apply to different qubits, they will be compiled one after the other.

        Returns: next usable even tick after these gates have been compiled.
        """
        for i, gate in enumerate(gates):
            assert len(gate.qubits) == gate_size
            gate_tick = tick + 2 * i
            circuit.add_instruction(gate_tick, gate)
            if noise is not None:
                noise_instruction = noise.instruction(gate.qubits)
                circuit.add_instruction(gate_tick + 1, noise_instruction)
        # Return the next usable even tick
        return tick + 2 * len(gates)

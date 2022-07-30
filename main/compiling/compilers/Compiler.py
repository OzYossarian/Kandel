from abc import abstractmethod, ABC
from typing import List, Dict, Tuple
from main.building_blocks.Check import Check
from main.building_blocks.detectors.Detector import Detector
from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.building_blocks.pauli.utils import plus_one_eigenstates
from main.compiling.Instruction import Instruction
from main.QPUs.QPU import QPU
from main.codes.Code import Code
from main.building_blocks.pauli.PauliLetter import PauliX, PauliZ, PauliY, PauliLetter
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli.Pauli import Pauli
from main.compiling.Circuit import Circuit
from main.compiling.compilers.Determiner import Determiner
from main.compiling.noise.models.NoNoise import NoNoise
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.syndrome_extraction.extractors.SyndromeExtractor import (
    SyndromeExtractor,
)
from main.enums import State
from main.utils.utils import xor
import stim


class Compiler(ABC):
    def __init__(
            self, noise_model: NoiseModel | None,
            syndrome_extractor: SyndromeExtractor,
            gate_set=("CNOT", "RZ", "MZ", "RX", "MX", "RY", "MY")):
        if noise_model is None:
            noise_model = NoNoise()
        self.noise_model = noise_model
        self.syndrome_extractor = syndrome_extractor
        self.state_init_instructions = {
            State.Zero: ["RZ"],
            State.One: ["RZ", "X"],
            State.Plus: ["RX"],
            State.Minus: ["RX", "Z"],
            State.I: ["RY"],
            State.MinusI: ["RY", "X"],
        }
        self.basis_measurements = {PauliX: "MX", PauliY: "MY", PauliZ: "MZ"}
        self.gate_set = gate_set

    def compile_qpu(
        self, qpu: QPU, layers: int, tick: int = 0, circuit: Circuit = None
    ):
        pass

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
            code, initial_states, initial_stabilizers
        )

        initial_layers = len(initial_detector_schedules)
        # initial_layers is the number of layers in which 'lid-only' detectors
        # exist.
        if initial_layers > layers:
            # TODO - bug here! initial_layers can be too big.
            raise ValueError(
                f"Requested that {layers} layer(s) are compiled, but code seems "
                f"to take {initial_layers} layer(s) to set up! Please increase "
                f"number of layers to compile"
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
            code,
        )

        return circuit.to_stim(self.noise_model)

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

        determiner = Determiner(code, self.state_init_instructions)
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
        self, initial_states: Dict[Qubit, State], tick: int, circuit: Circuit
    ):
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
                for name in self.state_init_instructions[state]
            ]
            circuit.initialise(tick, init_instructions)
            instructions_needed = len(init_instructions)
            # Add noise, if needed.
            if noise is not None:
                for i in range(len(init_instructions)):
                    noise_tick = tick + (2 * instructions_needed - 1)
                    circuit.add_instruction(noise_tick, noise.instruction([qubit]))

            ticks_needed = max(ticks_needed, 2 * instructions_needed)

        return tick + ticks_needed

    def compile_layer(
        self,
        layer: int,
        detector_schedule: List[List[Detector]],
        observables: List[LogicalOperator] | None,
        tick: int,
        circuit: Circuit,
        code: Code,
    ):
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
                check, round, self, tick, circuit
            )

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

        if observables is not None:
            observable_updates = code.update_logical_qubits(round)
            for observable in observables:
                circuit.measurer.add_to_logical_observable(
                    observable_updates[observable], observable, round
                )

        circuit.end_round(final_tick - 2)

        return final_tick

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
                zero = (
                    tuple([0 for _ in pauli.qubit.coords])
                    if isinstance(pauli.qubit.coords, tuple)
                    else 0
                )
                check = Check({zero: pauli}, pauli.qubit.coords)
                final_checks[pauli.qubit] = check

            # First, compile instructions for actually measuring the qubits.
            for pauli in final_measurements:
                self.measure_qubit(
                    pauli.qubit,
                    pauli.letter,
                    final_checks[pauli.qubit],
                    round,
                    tick,
                    circuit,
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
                final_checks, round, layer, code
            )
        else:
            final_detectors = self.compile_final_detectors_from_stabilizers(
                final_checks, final_stabilizers
            )

        # Finally, compile these detectors to the circuit.
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
            drum = Drum(stabilizer.lid, measurements, 0, stabilizer.anchor)
            final_detectors.append(drum)
        return final_detectors

    def compile_final_detectors_from_measurements(
        self, final_checks: Dict[Qubit, Check], round: int, layer: int, code: Code
    ):
        final_detectors = []
        for detector in code.detectors:
            open_lid, checks_measured = detector.has_open_lid(
                round - 1, layer - 1, code.schedule_length
            )
            if open_lid:
                # This detector can potentially be 'finished off', if our
                # final data qubit measurements are in the right bases.

                detector_checks = sorted(checks_measured, key=lambda check: -check[0])
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
                circuit.measurer.add_to_logical_observable(
                    logical_checks, observable, round
                )

    def measure_qubit(
        self,
        qubit: Qubit,
        basis: PauliLetter,
        check: Check,
        round: int,
        tick: int,
        circuit: Circuit,
    ):
        # TODO - generalise for native multi-qubit measurements.
        noise = self.noise_model.measurement
        params = noise.params if noise is not None else ()
        measurement_name = self.basis_measurements[basis]
        measurement = Instruction(
            [qubit], measurement_name, params, is_measurement=True
        )
        circuit.measure(measurement, check, round, tick)
        return tick + 2

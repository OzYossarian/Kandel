from abc import abstractmethod, ABC
from typing import List, Dict, Iterable, Union
from main.building_blocks.Check import Check
from main.building_blocks.detectors.Detector import Detector
from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.building_blocks.pauli.utils import plus_one_eigenstates
from main.codes.tic_tac_toe.FloquetColourCode import FloquetColourCode
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.codes.tic_tac_toe.gauge.GaugeHoneycombCode import GaugeHoneycombCode
from main.codes.tic_tac_toe.gauge.GaugeTicTacToeCode import GaugeTicTacToeCode
from main.compiling.Instruction import Instruction
from main.codes.Code import Code
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli.Pauli import Pauli
from main.compiling.Circuit import Circuit, RepeatBlock
from main.compiling.compilers.DetectorInitialiser import DetectorInitialiser
from main.compiling.noise.models.NoNoise import NoNoise
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.syndrome_extraction.extractors.SyndromeExtractor import (
    SyndromeExtractor,
)
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CnotExtractor import (
    CnotExtractor,
)
from main.utils.enums import State
from main.utils.types import Tick
from main.utils.utils import xor
from main.codes.tic_tac_toe.gauge.GaugeFloquetColourCode import GaugeFloquetColourCode
import stim


class Compiler(ABC):
    """Base class for all compilers.

    At the moment, this compiler can be used to create a memory experiment
    using the function compile_to_circuit.
    """

    def __init__(
            self,
            noise_model: NoiseModel = None,
            syndrome_extractor: SyndromeExtractor = None,
            initialisation_instructions: Dict[State, List[str]] = None,
            measurement_instructions: Dict[PauliLetter, List[str]] = None,
    ):
        # All initialisations must start with a reset, but can follow it with
        # other types of gates.
        # e.g. Initialising into the plus state can be implemented by
        # initialising into the zero state ('RZ') then doing a Hadamard ('H').
        if initialisation_instructions is not None:
            valid = all([
                instructions[0][0] == "R"
                for instructions in initialisation_instructions.values()])
            if not valid:
                raise ValueError(
                    "All initialisation instructions should start with a "
                    f"reset gate. Instead, got the following: "
                    f"{initialisation_instructions}")

        # Similarly, all measurements must end with an actual measurement, but
        # can be preceded by some other gates.
        # e.g. Measuring in the X-basis can be implemented by doing a Hadamard
        # ('H') then measuring in the Z-basis ('MZ')
        if measurement_instructions is not None:
            valid = all([
                instructions[-1][0] == "M"
                for instructions in measurement_instructions.values()])
            if not valid:
                raise ValueError(
                    "All measurement instructions should end with a "
                    f"measurement gate. Instead, got the following: "
                    f"{measurement_instructions}")

        # Configure defaults
        if noise_model is None:
            noise_model = NoNoise()
        if syndrome_extractor is None:
            # Fall back to some general syndrome extractor. But note that
            # without providing an ordering, this might try to place two
            # controlled gates on the same qubit at once, which will raise
            # an error.
            syndrome_extractor = CnotExtractor()
        if initialisation_instructions is None:
            initialisation_instructions = {
                State.Zero: ["RZ"],
                State.One: ["RZ", "X"],
                State.Plus: ["RX"],
                State.Minus: ["RX", "Z"],
                State.I: ["RY"],
                State.MinusI: ["RY", "X"]}
        if measurement_instructions is None:
            measurement_instructions = {
                PauliLetter('X'): ["MX"],
                PauliLetter('Y'): ["MY"],
                PauliLetter('Z'): ["MZ"]}

        self.noise_model = noise_model
        self.syndrome_extractor = syndrome_extractor
        self.initialisation_instructions = initialisation_instructions
        self.measurement_instructions = measurement_instructions

    def check_validity_of_inputs(
        self,
        code: Code,
        initial_states: Dict[Qubit, State] = None,
        initial_stabilizers: List[Stabilizer] = None,
        final_measurements: List[Pauli] = None,
        final_stabilizers: List[Stabilizer] = None,
        observables: List[LogicalOperator] = None,
    ):

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

        if final_stabilizers is not None:
            # Checks within final stabilizers should be things we'll
            # actually measure as part of the code's check schedule.
            self._assert_final_stabilizers_valid(final_stabilizers, code)

        compile_final_round = \
            final_measurements is not None or final_stabilizers is not None

        if observables is not None and not compile_final_round:
            if isinstance(code, TicTacToeCode) or isinstance(code, GaugeTicTacToeCode):
                pass
            else:
                raise ValueError(
                    "Can't measure any observables if no method is given "
                    "for performing final measurements! Please provide one of "
                    "final_measurements or final_stabilizers, "
                    "or set observables to None.")

    def compile_to_circuit(
        self,
        code: Code,
        total_rounds: int,
        initial_states: Dict[Qubit, State] = None,
        initial_stabilizers: List[Stabilizer] = None,
        final_measurements: List[Pauli] = None,
        final_stabilizers: List[Stabilizer] = None,
        observables: List[LogicalOperator] = None,
    ) -> Circuit:
        """ Compiles a circuit for a given code.

        Args:
            code: The code to compile a circuit for.
            total_rounds: The number of rounds to compile.
            initial_states: The initial states of the data qubits. If not
                provided, will use initial_stabilizers to determine the
                initial state.
            initial_stabilizers: If initial_states is not provided,
                this can be used to determine the initial states of the data
                qubits.
            final_measurements: The measurements to perform at the end of the
                circuit. If not provided, will use final_stabilizers to
                determine the measurements. If the code is a tic-tac-toe code,
                the measurements will be determined by the pauli-letter of the 
                observables at the last round.
            final_stabilizers: If final_measurements is not provided,
                this can be used to determine the measurements to perform at
                the end of the circuit.
            observables: 
                The observables to include in the circuit.
        """
        self.check_validity_of_inputs(
            code, initial_states, initial_stabilizers, final_measurements, final_stabilizers, observables
        )
        initial_detector_schedules, tick, circuit = self.compile_initialisation(
            code, initial_states, initial_stabilizers)

        initialization_layers = len(initial_detector_schedules)
        # initial_layers is the number of layers in which 'lid-only'
        # detectors exist.
        if initialization_layers * code.schedule_length > total_rounds:
            raise ValueError(
                f"The number of layers required to set up the code is "
                f"greater than the number of layers to compile!"
                f"Requested that {total_rounds} round(s) are compiled, but code "
                f"seems to take {initialization_layers * code.schedule_length} round(s) to set up.")

        # Compile these initial layers.
        for layer, detector_schedule in enumerate(initial_detector_schedules):
            tick = self.compile_layer(
                layer, detector_schedule, observables, tick, circuit, code
            )

        # Compile the remaining layers.
        round = code.schedule_length * initialization_layers
        while round < total_rounds:
            tick = self.compile_round(
                round,
                round % code.schedule_length,
                code.detector_schedule,
                observables,
                tick,
                circuit,
                code,
            )
            round += 1

        # For tic-tac-toe codes, which measurements need to be performed at the end depends on the number of rounds.
        # Only after compilition the at_round function contains the pauli letter of the observable.
        # That is why we do this here.
        if final_stabilizers is None and final_measurements is None:
            # We are assuming that there is only one observable in the list.
            pauli_letter_observable = observables[0].at_round(round-1)[
                0].letter.letter

            final_measurements = [Pauli(qubit, PauliLetter(pauli_letter_observable))
                                  for qubit in code.data_qubits.values()]

        # Finish with data qubit measurements, and use these to reconstruct
        # some detectors.
        self.compile_final_measurements(
            final_measurements,
            final_stabilizers,
            observables,
            round,
            tick,
            circuit,
            code)

        return circuit

    def compile_to_circuit_for_loop(
            self,
            code: Code,
            total_rounds: int,
            initial_states: Dict[Qubit, State] = None,
            initial_stabilizers: List[Stabilizer] = None,
            final_measurements: List[Pauli] = None,
            final_stabilizers: List[Stabilizer] = None,
            observables: List[LogicalOperator] = None,
    ) -> Circuit:
        """
        TODO explain total rounds
        """

        self.check_validity_of_inputs(
            code, initial_states, initial_stabilizers, final_measurements, final_stabilizers, observables
        )
        initial_detector_schedules, tick, circuit = self.compile_initialisation(
            code, initial_states, initial_stabilizers)

        initialization_layers = len(initial_detector_schedules)
        # initial_layers is the number of layers in which 'lid-only'
        # detectors exist.
        if initialization_layers * code.schedule_length > total_rounds:
            raise ValueError(
                f"The number of layers required to set up the code is "
                f"greater than the number of layers to compile!"
                f"Requested that {total_rounds} round(s) are compiled, but code "
                f"seems to take {initialization_layers * code.schedule_length} round(s) to set up.")

        # Compile these initial layers.
        for layer, detector_schedule in enumerate(initial_detector_schedules):
            tick = self.compile_layer(
                layer, detector_schedule, observables, tick, circuit, code
            )

        # Compile the remaining layers.
        tick_at_start_of_for_loop = tick
        for_loop_repetitions = (
            total_rounds - initialization_layers * code.schedule_length)//code.schedule_length

        # final round of for loop
        round = code.schedule_length * initialization_layers
        while round < (code.schedule_length * initialization_layers + code.schedule_length):
            tick = self.compile_round(
                round,
                round % code.schedule_length,
                code.detector_schedule,
                observables,
                tick,
                circuit,
                code,
            )
            round += 1

        tick_at_end_of_for_loop = tick
        for tick_in_for_loop in range(tick_at_start_of_for_loop, tick_at_end_of_for_loop):
            circuit.repeat_blocks[tick_in_for_loop] = [
                tick_at_start_of_for_loop,
                tick_at_end_of_for_loop,
                for_loop_repetitions
            ]

        # need to compile some rounds after completion of for loop
        while round < (total_rounds - (for_loop_repetitions - 1) * code.schedule_length):
            tick = self.compile_round(
                round,
                round % code.schedule_length,
                code.detector_schedule,
                observables,
                tick,
                circuit,
                code,
            )
            round += 1

        # Finish with data qubit measurements, and use these to reconstruct
        # some detectors.
        if isinstance(code, TicTacToeCode) or isinstance(code, GaugeTicTacToeCode):
            pauli_letter_observable = observables[0].at_round(round-1)[
                0].letter.letter

            final_measurements = [Pauli(qubit, PauliLetter(pauli_letter_observable))
                                  for qubit in code.data_qubits.values()]

        self.compile_final_measurements(
            final_measurements,
            final_stabilizers,
            observables,
            round,
            tick,
            circuit,
            code)

        return circuit

    def compile_final_layer(
        self,
        layer: int,
        detector_schedule: List[List[Detector]],
        stability_observable_rounds: List[int],
        tick: int,
        circuit: Circuit,
        code: Code,
    ) -> int:
        obs = LogicalOperator([])
        for relative_round in range(code.schedule_length):
            # Compile one round of checks, and note down the final tick
            # used, then start the next round of checks from this tick.
            round = layer * code.schedule_length + relative_round

            if relative_round in stability_observable_rounds:
                tick = self.compile_final_round(
                    round,
                    relative_round,
                    detector_schedule,
                    obs,
                    tick,
                    circuit,
                    code,
                )
            else:
                tick = self.compile_round(
                    round,
                    relative_round,
                    code.check_schedule,
                    detector_schedule,
                    None,
                    tick,
                    circuit,
                    code,
                )

        # round = layer * code.schedule_length + relative_round + 1
        return (tick)

    def compile_final_round(
        self,
        round: int,
        relative_round: int,
        detector_schedule: List[List[Detector]],
        observable: Union[List[LogicalOperator], None],
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

        # Next note down any detectors we'll need to compile at this round.
        detectors = detector_schedule[relative_round]

        circuit.measurer.add_detectors(detectors, round)

        circuit.measurer.multiply_observable(
            checks, observable, round
        ),
        circuit.end_round(tick - 2)

        return tick

    def compile_to_stim(
        self,
        code: Code,
        total_rounds: int,
        initial_states: Dict[Qubit, State] = None,
        initial_stabilizers: List[Stabilizer] = None,
        final_measurements: List[Pauli] = None,
        final_stabilizers: List[Stabilizer] = None,
        observables: List[LogicalOperator] = None,
    ) -> stim.Circuit:
        circuit = self.compile_to_circuit(
            code=code,
            total_rounds=total_rounds,
            initial_states=initial_states,
            initial_stabilizers=initial_stabilizers,
            final_measurements=final_measurements,
            final_stabilizers=final_stabilizers,
            observables=observables)
        return (circuit.to_stim(self.noise_model.idling, self.noise_model.resonator_idle))

    def compile_initialisation(
            self,
            code: Code,
            initial_states: Union[Dict[Qubit, State], None],
            initial_stabilizers: Union[List[Stabilizer], None],
    ):
        """Compiles the initialisation of the circuit.

        Args:
            code: The code to compile an initialisation circuit for.
            initial_states: The initial states of the data qubits. If not
                provided, will use initial_stabilizers to determine the
                initial state.
            initial_stabilizers: If initial_states is not provided,
                this can be used to determine the initial states of the data
                qubits.

        Returns:
            A tuple containing:
                - A list of detector schedules, one for each layer in which
                    'lid-only' detectors exist.
                - The tick at which the circuit should start.
                - The circuit to compile the initialisation onto.
        """
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

        if set(initial_states.keys()) != set(code.data_qubits.values()):
            raise ValueError(
                f"Set of data qubits whose initial states were either given "
                f"or could be determined differs from the set of all data "
                f"qubits. Please give a complete set of desired initial states "
                f"or desired stabilizers for the first round of measurements. "
                f"Set of all data qubits is {list(code.data_qubits.values())}. "
                f"Set of data qubits whose initial states could be determined "
                f"is {list(initial_states.keys())}")

        # Initialise data qubits, and set the 'current' tick to be the tick
        # we're on after all data qubits have been initialised.
        tick = self.initialize_qubits(initial_states, tick, circuit)

        # In the first few rounds (or even layers), there might be some
        # non-deterministic detectors that need removing.

        detector_initialiser = DetectorInitialiser(code, self)
        initial_detector_schedules = detector_initialiser.get_initial_detectors(
            initial_states, initial_stabilizers)

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
            qubit: plus_one_eigenstates[pauli.letter]
            for qubit, pauli in paulis.items()}
        return initial_states

    def _get_paulis(self, stabilizers: List[Stabilizer]):
        paulis = {}
        for stabilizer in stabilizers:
            # Whether the stabilizer has sign +1 or -1, we can use Paulis
            # with all +1 signs. This is because when these Paulis are later
            # used to build a detector, it does not matter whether the
            # detector's expected outcome is 1 or -1. It only matters that
            # the expected outcome is deterministic.
            for pauli in stabilizer.product.paulis:
                positive_letter = PauliLetter(pauli.letter.letter)
                positive_pauli = Pauli(pauli.qubit, positive_letter)
                existing = paulis.get(pauli.qubit, None)
                if existing is None:
                    paulis[pauli.qubit] = positive_pauli
                elif existing != positive_pauli:
                    raise ValueError(
                        f"The desired stabilizers are inconsistent! "
                        f"Qubit {pauli.qubit} resolves to both "
                        f"{existing.letter} and {pauli.letter}.")
        return paulis

    def initialize_qubits(
            self,
            initial_states: Dict[Qubit, State],
            tick: int,
            circuit: Circuit,
            initialisation_instructions: Dict[State, List[str]] = None
    ) -> Tick:
        """Initialises the data qubits in the given states.

        Args:
            initial_states: The states to initialise the data qubits in.
            tick: The tick at which to start initialising the qubits.
            circuit: The circuit to initialise the qubits on.
            initialisation_instructions: The instructions to use to initialise
                the qubits in the given states. If not provided, will use the
                default initialisation instructions specified in
                self.initialisation_instructions
        """
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
            if len(init_instructions) > 1:
                self.compile_gates(init_instructions[1:], tick + 2, circuit)
            ticks_needed = max(ticks_needed, 2 * len(init_instructions))

        return tick + ticks_needed

    def compile_layer(
            self,
            layer: int,
            detector_schedule: List[List[Detector]],
            observables: Union[List[LogicalOperator], None],
            tick: int,
            circuit: Circuit,
            code: Code
    ) -> int:
        """
        Compiles one layer of a code's entire check schedule.

        Args:
            layer: The layer of the check schedule to compile.
            detector_schedule: The detector schedule to compile. This is not
            fixed as the detector schedule of the first round is different
            then subsequent rounds.
            observables: The logical observables to measure.
            tick: The tick at which to start compiling the layer.
            circuit: The circuit to compile the layer on.
            code: The code to compile the layer for .

        Returns:
            The tick at which the last gates of the layer were compiled.
        """
        for relative_round in range(code.schedule_length):

            # Compile one round of checks, and note down the final tick
            # used, then start the next round of checks from this tick.
            round = layer * code.schedule_length + relative_round

            tick = self.compile_round(
                round,
                relative_round,
                #                code.check_schedule,
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
            observables: Union[List[LogicalOperator], None],
            tick: int,
            circuit: Circuit,
            code: Code,
    ):
        """ Compile one round of the code's check schedule.

        Args:
            round: The round of the code to compile.
            relative_round: The round relative to the length of the code schedule to compile.
            detector_schedule: The detector schedule to compile.
            observables: The logical observables to measure.
            tick: The tick to start compiling at.
            circuit: The circuit to compile to.
            code: The code to compile for.

        Returns:
            The tick after the round has been compiled.
        """
        self.add_start_of_round_noise(tick - 1, circuit, code)

        # First compile the syndrome extraction circuits for the checks.
        checks = code.check_schedule[relative_round]
        tick = self.syndrome_extractor.extract_checks(
            checks, round, tick, circuit, self
        )

        # Next note down any detectors we'll need to compile at this round.
        detectors = detector_schedule[relative_round]
        circuit.measurer.add_detectors(detectors, round)

        # And likewise note down any observables that need updating.
        if observables is not None:
            for observable in observables:
                checks_to_multiply_in = observable.update(round)

                circuit.measurer.multiply_observable(
                    checks_to_multiply_in, observable, round)

        circuit.end_round(tick - 2)
        return tick

    def add_start_of_round_noise(self, tick: int, circuit: Circuit, code: Code):
        noise = self.noise_model.data_qubit_start_round
        if noise is not None:
            for qubit in code.data_qubits.values():
                circuit.add_instruction(tick, noise.instruction([qubit]))

    def compile_final_schedule(
            self,
            observables: Union[List[LogicalOperator], None],
            layer: int,
            tick: int,
            circuit: Circuit,
            code: Code,
    ):
        for relative_round in range(len(code.final_check_schedule)-1):
            # Compile one round of checks, and note down the final tick
            # used, then start the next round of checks from this tick.
            round = layer * code.schedule_length + relative_round
            tick = self.compile_round(
                round,
                relative_round,
                code.final_check_schedule,
                code.final_detector_schedule,
                observables,
                tick,
                circuit,
                code,
            )

        # First, compile instructions for actually measuring the qubits.
        paulis = [list(check.paulis.values())[0]
                  for check in code.final_check_schedule[-1]]
        self.measure_individual_qubits(
            paulis,
            code.final_check_schedule[-1], round+1, tick, circuit
        )

        detectors = code.final_detector_schedule[-1]
        circuit.measurer.add_detectors(detectors, round+1)

        # Finally, define the observables we want to measure
        final_checks = {}
        for pauli in paulis:
            check = Check([pauli], pauli.qubit.coords)
            final_checks[pauli.qubit] = check

        self.compile_final_logical_operators(
            observables, final_checks, round+1, circuit
        )

        # Compile the final measurements
        # final_measurements = code.final_check_schedule[-1]
        # self.compile_final_measurements(
        #    final_measurements, None, observables, layer, tick, circuit, code
        # )

        return tick

    def compile_final_measurements(
            self,
            final_measurements: Union[List[Pauli], None],
            final_stabilizers: Union[List[Stabilizer], None],
            observables: Union[List[LogicalOperator], None],
            round: int,
            tick: int,
            circuit: Circuit,
            code: Code,
    ):
        """Compile the final measurements of the circuit.

        This method is called at the end of compile_to_circuit. It is
        assumed that the circuit has already been compiled up to this point,
        and that the circuit is in the ground state of the final stabilizers.

        Args:
            final_measurements: The single qubit Paulis to measure at the end
                of the circuit. If None, the final measurements depend on the
                given final stabilizers.
            final_stabilizers: The stabilizers to measure at the end of the
                circuit. If None, the final measurements are given by
                final_measurements. Note that not both final_measurements and
                final_stabilizers can be None.
            logical_observables: The logical observables to construct from the
                final measurements.
            round: The round of the circuit to compile.
            tick: The tick to start compiling at.
            circuit: The circuit to compile to.
            code: The code to compile for.

        Returns:
            The tick after the final measurements have been compiled.
        """
        # TODO - allow measurements other than single data qubits
        #  measurements at the end? e.g. Pauli product measurements.
        if final_stabilizers is not None:
            final_measurements = self.get_measurement_bases(final_stabilizers)

        elif final_measurements is not None:
            # A single qubit measurement is just a weight-1 check, and writing
            # them as checks rather than Paulis fits them into the same framework
            # as other measurements.
            final_checks = {}
            for pauli in final_measurements:
                check = Check([pauli], pauli.qubit.coords)
                final_checks[pauli.qubit] = check
            # A hack!
            if isinstance(code, TicTacToeCode) or isinstance(code, GaugeTicTacToeCode):
                final_pauli_letters = {
                    pauli.letter for pauli in final_measurements}
                if len(final_pauli_letters) > 1:
                    raise ValueError(
                        f"All final measurements must have the same letter. "
                        f"Instead, got: "f"{final_measurements}.")
                pauli_letter = final_pauli_letters.pop()
                route_final_letter = code.tic_tac_toe_route[(
                    round-1) % code.schedule_length][1]
                if (pauli_letter == route_final_letter):
                    add_small_detectors = True
                else:
                    add_small_detectors = False
            else:
                add_small_detectors = False
            # First, compile instructions for actually measuring the qubits.
            self.measure_individual_qubits(
                final_measurements, final_checks.values(), round, tick, circuit
            )
            # Now try to use these as lids for any detectors that at this point
            # have a floor but no lid.
            self.compile_final_detectors(
                final_checks, final_stabilizers, round, circuit, code, add_small_detectors
            )
            # Finally, define the observables we want to measure
            self.compile_final_logical_operators(
                observables, final_checks, round, circuit
            )

    def compile_final_detectors(
            self,
            final_checks: Union[Dict[Qubit, Check], None],
            final_stabilizers: Union[List[Stabilizer], None],
            round: int,
            circuit: Circuit,
            code: Code,
            add_small_detectors: bool = False
    ):
        if final_stabilizers is None:
            final_detectors = self.compile_final_detectors_from_measurements(
                final_checks, round, code, add_small_detectors)
        else:
            final_detectors = self.compile_final_detectors_from_stabilizers(
                final_checks, final_stabilizers, code)

        # Finally, compile these detectors to the circuit.
        circuit.measurer.add_detectors(final_detectors, round)

    def compile_final_detectors_from_stabilizers(
            self, final_checks: Dict[Qubit, Check],
            final_stabilizers: List[Stabilizer],
            code: Code):

        # Note - no need for extra validation here. We checked earlier that
        # the final stabilizers actually consist of checks from the code's
        # check schedule. And we derived the required single qubit data
        # measurements from these final stabilizers.
        final_detectors = []
        for stabilizer in final_stabilizers:
            qubits = [pauli.qubit for pauli in stabilizer.product.paulis]
            measurements = [(0, final_checks[qubit]) for qubit in qubits]
            floor = [
                # Figure out how many rounds ago each check was measured
                (stabilizer.end + t - code.schedule_length, check)
                for (t, check) in
                stabilizer.timed_checks]
            drum = Drum(floor, measurements, 0, stabilizer.anchor)
            final_detectors.append(drum)
        return final_detectors

    def get_factor_to_check_for_open_lid(self, final_checks, code, round):
        if isinstance(code, GaugeHoneycombCode) == False:
            return (0)

        current_letter = code.tic_tac_toe_route[round %
                                                code.schedule_length][1].letter
        final_check_letter = list(final_checks.values())[0].product.word.word
        previous_letter = code.tic_tac_toe_route[(round - 1) %
                                                 code.schedule_length][1].letter
        if current_letter != final_check_letter and current_letter == previous_letter:
            n = 1
            while True:
                if code.tic_tac_toe_route[(round + n) % code.schedule_length][1].letter != current_letter:
                    break
                n += 1
            return n

        else:
            return 0

    def compile_final_detectors_from_measurements(
            self, final_checks: Dict[Qubit, Check], round: int, code: Code, add_small_detectors: bool = False):
        final_detectors = []
        for detector in code.detectors:

            # should be round - 1 + n, where n is the number of same measurements that in the regular schedule have been skipped
            # so there are not enough "has open lid"
            n = self.get_factor_to_check_for_open_lid(
                final_checks, code, round)
            open_lid, detector_checks_measured = detector.has_open_lid(
                round - 1 + n, code.schedule_length)

            if open_lid:

                # This detector can potentially be 'finished off', if our
                # final data qubit measurements are in the right bases. First,
                # calculate the product of the detector's checks that have
                # actually been measured.
                detector_checks_measured = sorted(
                    detector_checks_measured,
                    key=lambda timed_check: -timed_check[0])

                detector_product_measured = PauliProduct([
                    pauli
                    for _, check in detector_checks_measured
                    for pauli in check.paulis.values()])

                # Restrict now just to the qubits that are actually involved
                # in the checks measured so far. Sort them just for
                # reproducibility in tests.
                detector_qubits = {
                    pauli.qubit
                    for pauli in detector_product_measured.paulis}
                detector_qubits = sorted(
                    detector_qubits, key=lambda qubit: qubit.coords)

                # Now calculate the product of the measurements on these qubits.
                measurements = [
                    list(final_checks[data_qubit].paulis.values())[0]
                    for data_qubit in detector_qubits]
                measurement_product = PauliProduct(measurements)

                if detector_product_measured.equal_up_to_sign(measurement_product):

                    floor = []
                    for t, check in detector_checks_measured:

                        expected_lid_end = (
                            round//code.schedule_length)*code.schedule_length + detector.lid_end
                        actual_lid_end = round

                        if expected_lid_end < actual_lid_end:
                            expected_lid_end += code.schedule_length
                        difference = expected_lid_end - actual_lid_end

                        floor_t = t + difference

                        if floor_t == -1 + n:
                            floor_t -= n

                        floor.append((floor_t, check))

                    lid = [(0, final_checks[qubit])
                           for qubit in detector_qubits]

                    new_drum = Drum(floor, lid, (round %
                                    code.schedule_length), detector.anchor)

                    # because gauge css floquet codes tries to add hexagonal detectors of consecutive rounds
                    if isinstance(code, GaugeFloquetColourCode) or isinstance(code, FloquetColourCode):
                        if (new_drum.end - new_drum.start) == 1:
                            pass
                        else:
                            final_detectors.append(new_drum)
                    else:
                        final_detectors.append(new_drum)

        if add_small_detectors:
            for check in code.check_schedule[(round-1) % code.schedule_length]:
                floor = [(-1, check)]
                floor_qubits = [pauli.qubit for pauli in check.paulis.values()]
                lid = [(0, final_checks[qubit])
                       for qubit in floor_qubits]
                final_detectors.append(
                    Drum(floor, lid, (round % code.schedule_length), None))
        return final_detectors

    def compile_final_logical_operators(
            self,
            observables: Union[List[LogicalOperator], None],
            final_checks: Union[Dict[Qubit, Check], None],
            round: int,
            circuit: Circuit,
    ):
        # The Paulis that currently constitute the logical operators
        # we want to measure should be a subset of the final individual data
        # qubit measurements.
        if observables is not None:
            for observable in observables:
                observable_checks = []
                for observable_pauli in observable.at_round(round - 1):
                    # Just double check that what we measured is actually what we
                    # want to use to form the logical operator.
                    check = final_checks[observable_pauli.qubit]
                    check_pauli = list(check.paulis.values())[0]
                    if check_pauli.letter.letter != observable_pauli.letter.letter:
                        raise ValueError(
                            f"Expected to include a final measurement of "
                            f"{observable_pauli} into an observable, but the "
                            f"final measurement at this qubit was instead "
                            f"{check_pauli}!")
                    observable_checks.append(check)

                # Compile to the circuit.
                circuit.measurer.multiply_observable(
                    observable_checks, observable, round
                )
    # TODO - generalise for native multi-qubit measurements.

    def measure_individual_qubits(
            self,
            paulis: Iterable[Pauli],
            checks: Iterable[Check],
            round: int,
            tick: Tick,
            circuit: Circuit,
            measurement_instructions: Dict[PauliLetter, List[str]] = None,
    ):
        """

        Args:
            paulis:
            checks: _description_
            round: _description_
            tick: _description_
            circuit: _description_
            measurement_instructions: _description_. Defaults to None.

        Returns:
            _description_
        """
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
                for name in measurement_instructions[pauli.letter]]
            # Compile gates needed before the measurement
            gates = instructions[:-1]
            measurement_tick = self.compile_gates(gates, tick, circuit)
            # Now do the actual measurement.
            measurement = instructions[-1]
            measurement.is_measurement = True
            measurement.params = measurement_noise.params \
                if measurement_noise is not None \
                else ()
            circuit.measure(measurement, check, round, measurement_tick)

            ticks_needed = max(ticks_needed, 2 * len(instructions))

        return tick + ticks_needed

    def compile_gates(
            self, gates: List[Instruction], tick: Tick, circuit: Circuit
    ) -> Tick:
        """For compiling a list of gates sequentially. i.e. Even if the gates
        apply to different qubits, they will be compiled one after the other.

        Args:
            gates: List of gates to compile.
            tick: Tick to start compiling from.
            circuit: Circuit to compile to.

        Returns: next usable even tick after these gates have been compiled.
        """

        for i, gate in enumerate(gates):
            gate_tick = tick + 2 * i
            circuit.add_instruction(gate_tick, gate)
            gate_size = len(gate.qubits)
            if gate_size not in [1, 2]:
                raise ValueError(
                    f'Can only compile one- or two-qubit gates.'
                    f'Instead, was asked to compile the following: {gate}.')
            noise = self.noise_model.one_qubit_gate \
                if gate_size == 1 \
                else self.noise_model.two_qubit_gate

            if noise is not None:
                noise_instruction = noise.instruction(gate.qubits)
                circuit.add_instruction(gate_tick + 1, noise_instruction)
        # Return the next usable even tick

        return tick + 2 * len(gates)

    def _assert_final_stabilizers_valid(
            self, final_stabilizers: List[Stabilizer], code: Code):
        for stabilizer in final_stabilizers:
            for t, check in stabilizer.timed_checks:
                expected_round = (stabilizer.end + t) % code.schedule_length
                if check not in code.check_schedule[expected_round]:
                    raise ValueError(
                        f"Requested that a final detector is built using a "
                        f"check that isn't in the code's check schedule! "
                        f"The check is {check}, and is part of stabilizer "
                        f"{stabilizer}. The code's check schedule is "
                        f"{code.check_schedule}.")

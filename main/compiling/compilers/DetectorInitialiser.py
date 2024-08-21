from __future__ import annotations

import math
from collections import defaultdict
from typing import List, Dict, TYPE_CHECKING, Tuple, Union

import stim

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.detectors.Detector import Detector, TimedCheck
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.codes.Code import Code
from main.compiling.Circuit import Circuit
from main.compiling.Instruction import Instruction
from main.utils.types import Tick
from main.codes.tic_tac_toe.gauge.GaugeFloquetColourCode import GaugeFloquetColourCode

if TYPE_CHECKING:
    from main.compiling.compilers.Compiler import Compiler
from main.utils.enums import State


class DetectorInitialiser:
    def __init__(self, code: Code, compiler: Compiler):
        """
        A class for handling the logic around compiling detectors for the
        first round(s) of a code. In the first round(s), checks that are
        deterministic in later rounds may actually be non-deterministic,
        depending on how the data qubits are initialised. e.g. In the surface
        code, if all data qubits are initialised in the zero state, then the
        XX...X checks are non-deterministic the first time they're measured.
        Thus we shouldn't use them as detectors. The ZZ...Z checks are
        deterministic, however, and using them as detectors allows us to
        correct errors that occur immediately after initialising the qubits.

        Logically this class could just be part of the base Compiler class,
        but it's separated here to avoid bloating that class. Indeed, it
        takes a compiler as an argument, so that it can use it to initialise
        qubits.

        Args:
            code: the code to be compiled
            compiler: the compiler that will be used to perform the rest of
                the compilation.
        """
        self.code = code
        self.compiler = compiler
        self.stim_pauli_targeters = {
            'X': stim.target_x,
            'Y': stim.target_y,
            'Z': stim.target_z}

    def get_initial_detectors(
            self, initial_states: Dict[Qubit, State],
            initial_stabilizers: Union[List[Stabilizer], None]
    ) -> List[List[List[Detector]]]:
        """
        Determine the detectors that should be measured in the first round(s).
        Initial states should always be provided. Initial stabilizers can also
        optionally be provided - these will then be used as detectors in the
        first round(s) of the code, replacing the detectors that would
        otherwise be used.

        Args:
            initial_states:
                the states in which the data qubits should be initialised.
            initial_stabilizers:
                detectors to be used in the first round(s) of the code,
                replacing the detectors from the usual schedule. As the name
                suggests, data qubits should be initialised such that these
                detectors are stabilizers in the first round(s).
        Returns:
            the initial detector schedules. That is, a nested list of
            detectors, where the list at index i specifies the detectors to
            be compiled in layer i. Within this list, the list at index j
            specifies the detectors to be compiled at the end of round j.
            The returned list will have length equal to the number of layers
            for which the detector logic differs from the usual detector
            logic.
        """
        # Create a circuit initialised in the given states
        tick, circuit = self.initialise_circuit(initial_states)

        # If we've been given initial stabilizers, stick them into the
        # initial detector schedule. Else, start with an empty schedule.
        if initial_stabilizers is not None:
            tick, initial_detector_schedule = self.use_stabilizers_as_detectors(
                initial_stabilizers, tick, circuit)
            round = len(initial_detector_schedule)
        else:
            initial_detector_schedule = {}
            round = 0

        min_floor_start = round + min(
            detector.floor_start for detector in self.code.detectors)
        done = min_floor_start >= 0

        # for gauge floquet codes we need to check this condition such that we don't miss small detectors at the start consisting of a single check
        if isinstance(self.code, GaugeFloquetColourCode):
            min_floor_start -= max(self.code.gauge_factors)

        while not done:
            round_detectors = self.simulate_round(round, tick, circuit)
            initial_detector_schedule[round] = round_detectors
            # If all floors start at a non-negative round, then we're done
            # with this special initialisation logic.
            min_floor_start += 1
            done = min_floor_start >= 0
            round += 1
            tick += 2

        # Now split the schedule into chunks of the right size.
        initial_detector_schedules = self.split_schedule(
            initial_detector_schedule)

        return initial_detector_schedules

    def split_schedule(
            self, initial_detector_schedule: Dict[int, List[Detector]]):
        """
        'Reshape' the initial detector schedule. Effectively the initial
        detector schedule right now is a list of lists of detectors (because
        its keys are just integers starting at 0). This method just groups
        the values into lists of size k, where k is the code's schedule
        length. e.g. Letting i below denote the list with key i, we take:
            [0, 1, ... , k, k+1, ..., 2k, 2k+1, ...]
        and turn it into:
            [[0, 1, ... , k], [k+1, ..., 2k], [2k+1, ...]]

        Args:
            initial_detector_schedule: schedule to reshape.

        Returns:
            reshaped detector schedule.
        """
        initial_rounds = len(initial_detector_schedule)
        initial_layers = math.ceil(initial_rounds / self.code.schedule_length)
        initial_detector_schedules = [[] for _ in range(initial_layers)]

        # Chunk up the initial schedule into layers.
        schedule = sorted(initial_detector_schedule.items())
        for round, round_detectors in schedule:
            layer = round // self.code.schedule_length
            initial_detector_schedules[layer].append(round_detectors)

        # Maybe pad out the final initial layer with the usual detectors.

        truncation = len(initial_detector_schedules[-1])
        if truncation < self.code.schedule_length:
            initial_detector_schedules[-1] += \
                self.code.detector_schedule[truncation:]

        return initial_detector_schedules

    def simulate_round(self, round: int, tick: Tick, circuit: Circuit):
        """
        Find out which detectors should be built given the previous round of
        checks, and measure the checks for this given round.
        Args:
            round: the current round
            tick: the current tick
            circuit: the circuit implementing the code for rounds up to but
                not including the current round
        Returns:
            detectors that should be built before the given round starts.
        """
        # First peek at the expectation of each potential lid-only
        # detector and see which are deterministic.
        stim_circuit = circuit.to_stim(
            idling_noise=None, track_coords=False, track_progress=False)
        simulator = stim.TableauSimulator()
        simulator.do(stim_circuit)
        round_detectors = self.get_round_detectors(
            round, circuit, simulator)

        # Now compile the checks we would be measuring in this round,
        # in preparation for looking for deterministic detectors next
        # round. Use product measurements for simplicity.
        self.measure_checks(round, tick, circuit)

        return round_detectors

    def use_stabilizers_as_detectors(
            self, initial_stabilizers: List[Stabilizer], tick: int,
            circuit: Circuit
    ) -> Tuple[Tick, Dict[int, List[Detector]]]:
        """
        Set the given initial stabilizers to be detectors, and measure the
        checks for the rounds spanned by these stabilizers.

        Args:
            initial_stabilizers: stabilizers to be used as detectors in
                these initial round(s)
            tick: the current tick.
            circuit: the circuit initialising the code's data qubits.

        Returns:
            tick: the next usable tick
            initial_detector_schedule: lists of detectors to be built in
                these initial round(s), keyed by the first round at which
                they can be built
        """
        # Use these stabilizers as detectors in the initial schedule.
        initial_detector_schedule = defaultdict(list)
        for stabilizer in initial_stabilizers:
            initial_detector_schedule[stabilizer.end].append(stabilizer)

        # Measure the checks for the rounds spanned by these stabilizers.
        for round in range(len(initial_detector_schedule)):
            self.measure_checks(round, tick, circuit)
            tick += 2

        return tick, initial_detector_schedule

    def get_round_detectors(
            self, round: int, circuit: Circuit, simulator:
            stim.TableauSimulator):
        """
        Find out which detectors from the code's detector schedule would be
        deterministic at this round.

        Args:
            round: the current round
            circuit: the circuit implementing the code up to and including
                the given round
            simulator: the corresponding stim simulator for the given circuit.

        Returns:
            detectors to be used after the given round
        """
        layer, relative_round = divmod(round, self.code.schedule_length)
        shift = layer * self.code.schedule_length
        round_detectors = []
        for drum in self.code.detector_schedule[relative_round]:
            assert drum.end == relative_round
            if drum.floor_start + shift >= 0:
                # This detector is always going to be comparing a floor
                # with a lid, so should always be deterministic.
                round_detectors.append(drum)
            else:
                timed_checks = drum.checks_at_or_after(
                    0, self.code.schedule_length)
                if self.is_deterministic(timed_checks, circuit, simulator):
                    # This detector should become a 'lid-only' detector
                    # in this layer.
                    lid_only = Stabilizer(
                        timed_checks, relative_round, drum.anchor)
                    round_detectors.append(lid_only)
        return round_detectors

    def measure_checks(self, round: int, tick: int, circuit: Circuit):
        """
        Measure the checks for the given round. Use Pauli product
        measurements for simplicity.

        Args:
            round: the current round
            tick: the current tick
            circuit: the circuit implementing the code up to but not
                including the given round
        """
        relative_round = round % self.code.schedule_length
        for check in self.code.check_schedule[relative_round]:
            targets = self.product_measurement_targets(check, circuit)
            qubits = [pauli.qubit for pauli in check.paulis.values()]
            measurement = Instruction(
                qubits, 'MPP', targets=targets, is_measurement=True)
            circuit.measure(measurement, check, round, tick)

    def product_measurement_targets(
            self, check: Check, circuit: Circuit) -> List[stim.GateTarget]:
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
        targeter = self.stim_pauli_targeters[pauli.letter.letter]
        # We're guaranteed the check's product has sign in [1, -1], because
        # we force all checks to have a Hermitian product.
        invert = check.product.word.sign == -1
        # If inverting, it applies to the whole product, but equivalently can
        # just invert one qubit - may as well pick the first one.
        targets = [targeter(circuit.qubit_index(pauli.qubit), invert)]
        for pauli in paulis[1:]:
            targets.append(stim.target_combiner())
            targeter = self.stim_pauli_targeters[pauli.letter.letter]
            targets.append(targeter(circuit.qubit_index(pauli.qubit)))
        return targets

    def initialise_circuit(
            self, initial_states: Dict[Qubit, State]) -> Tuple[Tick, Circuit]:
        """
        Initialise a circuit with qubits in the given initial states.

        Args:
            initial_states: states to initialise qubits into.

        Returns:
            tick: next usable tick
            circuit: circuit representing the initialised qubits
        """
        circuit = Circuit()
        # This method returns the tick to be used by whatever the next
        # instructions are.
        tick = self.compiler.initialize_qubits(initial_states, 0, circuit)
        return tick, circuit

    def is_deterministic(
            self, timed_checks: List[TimedCheck], circuit: Circuit,
            simulator: stim.TableauSimulator
    ) -> bool:
        """
        Figure out whether the timed checks multiply to give an operator
        that, if measured, would give a deterministic outcome.

        Args:
            timed_checks:
                (t, check) pairs, where t is the round at which the check is
                measured, relative to the final check in the detector. In
                particular, t is always non-positive.
            circuit:
                circuit representing the compilation of the code so far.
            simulator:
                corresponding Stim simulator for the circuit.

        Returns:
            whether the given timed checks have a deterministic product.
        """
        timed_checks = sorted(
            timed_checks, key=lambda timed_check: -timed_check[0])
        product = PauliProduct([
            pauli
            for _, check in timed_checks
            for pauli in check.paulis.values()])
        string = self.to_pauli_string(product, circuit)
        expectation = simulator.peek_observable_expectation(string)
        return expectation in [1, -1]

    @ staticmethod
    def to_pauli_string(product: PauliProduct, circuit: Circuit):
        """
        Turn a PauliProduct into a stim.PauliString

        Args:
            product: product to convert
            circuit: circuit representing the compilation of the code so far
                (this contains indexes for the qubits, which is what Stim
                needs in order to create a PauliString).

        Returns:
            a PauliString corresponding to the given Pauli product.
        """
        string = ['_' for _ in range(len(circuit.qubits))]
        for pauli in product.paulis:
            string[circuit.qubit_index(pauli.qubit)] = pauli.letter.letter
        string = product.word.sign * stim.PauliString(''.join(string))
        return string

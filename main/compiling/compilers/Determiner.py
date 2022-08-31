from __future__ import annotations

import math
from collections import defaultdict
from typing import List, Dict, TYPE_CHECKING

import stim

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.detectors.Detector import Detector, TimedCheck
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.codes.Code import Code
from main.compiling.Circuit import Circuit
from main.compiling.Instruction import Instruction

if TYPE_CHECKING:
    from main.compiling.compilers.Compiler import Compiler
from main.compiling.noise.models.NoNoise import NoNoise
from main.enums import State


class Determiner:
    def __init__(self, code: Code, compiler: Compiler):
        self.code = code
        self.compiler = compiler
        self.stim_pauli_targeters = {
            'X': stim.target_x,
            'Y': stim.target_y,
            'Z': stim.target_z}

    def get_initial_detectors(
            self, initial_states: Dict[Qubit, State],
            initial_stabilizers: List[Stabilizer]):
        # Create a circuit initialised in the given states
        tick, circuit = self.initialise_circuit(initial_states)

        # If we've been given initial stabilizers, read them into the
        # initial schedule. Else, start with an empty schedule.
        if initial_stabilizers is not None:
            tick, initial_detector_schedule = self.process_stabilizers(
                initial_stabilizers, tick, circuit)
            round = len(initial_detector_schedule)
        else:
            initial_detector_schedule = defaultdict(list)
            round = 0

        # We're done when no more 'lid-only' detectors can occur
        min_floor_start = round + min(
            detector.floor_start for detector in self.code.detectors)
        done = min_floor_start >= 0

        no_noise = NoNoise()
        while not done:
            round_detectors = self.simulate_round(
                round, tick, circuit, no_noise)
            initial_detector_schedule[round].extend(round_detectors)

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
        initial_rounds = len(initial_detector_schedule)
        initial_layers = math.ceil(initial_rounds / self.code.schedule_length)
        initial_detector_schedules = [[] for _ in range(initial_layers)]

        # Chunk up the initial schedule into layers.
        length = self.code.schedule_length  # Handy shorthand
        schedule = sorted(initial_detector_schedule.items())
        for round, round_detectors in schedule:
            layer = round // length
            initial_detector_schedules[layer].append(round_detectors)

        # Maybe pad out the final initial layer with the usual detectors.
        truncation = len(initial_detector_schedules[-1])
        if truncation < self.code.schedule_length:
            initial_detector_schedules[-1] += \
                self.code.detector_schedule[truncation:]

        return initial_detector_schedules

    def simulate_round(self, round, tick, circuit, no_noise):
        # First peek at the expectation of each potential lid-only
        # detector and see which are deterministic.
        stim_circuit = circuit.to_stim(
            no_noise, track_coords=False, track_progress=False)
        simulator = stim.TableauSimulator()
        simulator.do(stim_circuit)
        round_detectors = self.get_round_detectors(
            round, circuit, simulator)

        # Now compile the checks we would be measuring in this round,
        # in preparation for looking for deterministic detectors next
        # round. Use product measurements for simplicity.
        self.measure_checks(round, tick, circuit)

        return round_detectors

    def process_stabilizers(
            self, initial_stabilizers: List[Stabilizer], tick: int,
            circuit: Circuit):
        # We assume that the given initial stabilizers replace any potential
        # 'lid-only' detectors that might otherwise have appeared in these
        # initial rounds. Then the first round we're actually interested in
        # is the one after the last given stabilizer.

        # Add the stabilizers into the initial schedule
        initial_detector_schedule = defaultdict(list)
        for stabilizer in initial_stabilizers:
            initial_detector_schedule[stabilizer.end].append(stabilizer)

        # Measure the checks for these rounds
        for round in range(len(initial_detector_schedule)):
            self.measure_checks(round, tick, circuit)
            tick += 2

        return tick, initial_detector_schedule

    def get_round_detectors(
            self, round: int, circuit: Circuit, simulator:
            stim.TableauSimulator):
        layer, relative_round = divmod(round, self.code.schedule_length)
        shift = layer * self.code.schedule_length
        round_detectors = []
        for detector in self.code.detector_schedule[relative_round]:
            assert detector.end == relative_round
            if detector.floor_start + shift >= 0:
                # This detector is always going to be comparing a floor
                # with a lid, so should always be deterministic.
                round_detectors.append(detector)
            else:
                timed_checks = detector.checks_at_or_after(
                    0, layer, self.code.schedule_length)
                if self.is_deterministic(timed_checks, circuit, simulator):
                    # This detector should become a 'lid-only' detector
                    # in this layer.
                    lid_only = Stabilizer(
                        timed_checks, relative_round, detector.anchor)
                    round_detectors.append(lid_only)
        return round_detectors

    def measure_checks(self, round: int, tick: int, circuit: Circuit):
        relative_round = round % self.code.schedule_length
        for check in self.code.check_schedule[relative_round]:
            qubits = [pauli.qubit for pauli in check.paulis.values()]
            targets = self.product_measurement_targets(check, circuit)
            measurement = Instruction(
                qubits, 'MPP', targets=targets, is_measurement=True)
            circuit.measure(measurement, check, round, tick)

    def product_measurement_targets(self, check: Check, circuit: Circuit):
        assert len(check.paulis) > 0
        product = PauliProduct(check.paulis.values())
        assert product.word.sign in [1, -1]
        # Do first pauli separately, then do the rest in a for loop.
        paulis = list(check.paulis.values())
        pauli = paulis[0]
        targeter = self.stim_pauli_targeters[pauli.letter.letter]
        invert = product.word.sign == -1
        # If inverting, it applies to the whole product, but equivalently can
        # just invert one qubit - may as well pick the first one.
        targets = [targeter(circuit.qubit_index(pauli.qubit), invert)]
        for pauli in paulis[1:]:
            targets.append(stim.target_combiner())
            targeter = self.stim_pauli_targeters[pauli.letter.letter]
            targets.append(targeter(circuit.qubit_index(pauli.qubit)))
        return targets

    def initialise_circuit(self, initial_states: Dict[Qubit, State]):
        circuit = Circuit()
        # This method returns the tick to be used by whatever the next
        # instructions are.
        tick = self.compiler.initialize_qubits(initial_states, 0, circuit)
        return tick, circuit

    def is_deterministic(
            self, timed_checks: List[TimedCheck], circuit: Circuit,
            simulator: stim.TableauSimulator):
        timed_checks = sorted(
            timed_checks, key=lambda timed_check: -timed_check[0])
        product = PauliProduct([
            pauli
            for _, check in timed_checks
            for pauli in check.paulis.values()])
        string = self.to_pauli_string(product, circuit)
        expectation = simulator.peek_observable_expectation(string)
        return expectation in [1, -1]

    def to_pauli_string(self, product: PauliProduct, circuit: Circuit):
        string = ['_' for _ in range(len(circuit.qubits))]
        for pauli in product.paulis:
            string[circuit.qubit_index(pauli.qubit)] = pauli.letter.letter
        string = product.word.sign * stim.PauliString(''.join(string))
        return string

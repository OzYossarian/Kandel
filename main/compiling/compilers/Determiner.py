from typing import List, Dict, Tuple

import stim

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.codes.Code import Code
from main.compiling.Circuit import Circuit
from main.compiling.Instruction import Instruction
from main.compiling.noise.models.NoNoise import NoNoise
from main.enums import State


class Determiner:
    def __init__(self):
        self.stim_pauli_targeters = {
            'X': stim.target_x,
            'Y': stim.target_y,
            'Z': stim.target_z}

    def get_initial_detectors(
            self, initial_states: Dict[Qubit, State],
            state_init_instructions: Dict[State, List[str]], code: Code):
        # TODO - set up some Stim tableau stuff, using generators defined by
        #  initial states. For now, workaround by doing it using a circuit.
        tick, circuit = self.initialise_circuit(
            initial_states, state_init_instructions)
        no_noise = NoNoise()

        # Proceed one round at a time, until no more 'open-bottom' (or
        # 'truncated') detectors can occur.
        layer = 0
        initial_detector_schedules = []
        min_floor_start = min(
            detector.floor_start for detector in code.detectors)
        done = min_floor_start >= 0

        while not done:
            # There's going to be some lid-only detectors in this round. Need
            # to figure out if any are non-deterministic and remove them.
            layer_detector_schedule = [[] for _ in range(code.schedule_length)]
            initial_detector_schedules.append(layer_detector_schedule)
            shift = layer * code.schedule_length

            for relative_round in range(code.schedule_length):
                round = relative_round + shift

                # First peek at the expectation of each potential lid-only
                # detector and see which are deterministic.
                stim_circuit = circuit.to_stim(
                    no_noise, track_coords=False, track_progress=False)
                simulator = stim.TableauSimulator()
                simulator.do(stim_circuit)
                round_detector_schedule = self.get_deterministic_detectors(
                    relative_round, shift, layer, circuit, code, simulator)
                layer_detector_schedule[relative_round] = round_detector_schedule

                # Now compile the checks we would be measuring in this round,
                # in preparation for looking for deterministic detectors next
                # round. Use product measurements for simplicity.
                self.measure_checks(round, relative_round, tick, circuit, code)

                tick += 2
                # If all floors start at a non-negative round, then we're done
                # with this special initialisation logic.
                min_floor_start += 1
                done = min_floor_start >= 0
            layer += 1

        # Now 'pad out' the rest of the last initial layer with the usual
        # detectors.
        if len(initial_detector_schedules) > 0:
            x = len(initial_detector_schedules[-1])
            initial_detector_schedules[-1] += code.detector_schedule[x:]

        return layer, initial_detector_schedules

    def get_deterministic_detectors(
            self, relative_round, shift, layer, circuit, code, simulator):
        round_detector_schedule = []
        for detector in code.detector_schedule[relative_round]:
            assert detector.lid_end == relative_round
            if detector.floor_start + shift >= 0:
                # This detector is always going to be comparing a floor
                # with a lid, so should always be deterministic.
                round_detector_schedule.append(detector)
            else:
                timed_checks = detector.checks_at_or_after(
                    0, layer, code.schedule_length)
                if self.is_deterministic(timed_checks, circuit, simulator):
                    # This detector should become a 'lid-only' detector
                    # in this layer.
                    lid_only = Stabilizer(
                        timed_checks, relative_round, detector.anchor)
                    round_detector_schedule.append(lid_only)
        return round_detector_schedule

    def measure_checks(self, round, relative_round, tick, circuit, code):
        for check in code.check_schedule[relative_round]:
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

    def initialise_circuit(self, initial_states, state_init_instructions):
        circuit = Circuit()
        # This method returns the tick to be used by whatever the next
        # instructions are.
        next_tick = 2
        for qubit, state in initial_states.items():
            instructions = [
                Instruction([qubit], name)
                for name in state_init_instructions[state]]
            circuit.initialise(0, instructions)
            next_tick = max(next_tick, 2 * len(instructions))
        return next_tick, circuit

    def is_deterministic(
            self, timed_checks: List[Tuple[int, Check]], circuit: Circuit,
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

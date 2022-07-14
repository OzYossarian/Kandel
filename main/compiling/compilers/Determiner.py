from typing import List, Dict

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

        # Proceed one layer at a time, until no more 'open-bottom' (or
        # 'truncated') detectors can occur.
        layer = 0
        layer_detector_schedules = []
        min_floor_start = min(
            detector.floor_start for detector in code.detectors)
        done = min_floor_start >= 0

        while not done:
            # There's going to be some lid-only detectors in this layer. Need
            # to figure out if any are non-deterministic and remove them.
            layer_detector_schedule = [[] for _ in range(code.schedule_length)]
            layer_detector_schedules.append(layer_detector_schedule)
            shift = layer * code.schedule_length

            for relative_round in range(code.schedule_length):
                round = relative_round + shift
                # First step is to compile the checks we would be measuring in
                # this round. Use product measurements for simplicity.
                for check in code.check_schedule[relative_round]:
                    qubits = [pauli.qubit for pauli in check.paulis]
                    targets = self.product_measurement_targets(check, circuit)
                    measurement = Instruction(
                        qubits, 'MPP', targets=targets, is_measurement=True)
                    circuit.measure(measurement, check, round, tick)

                # Now try to add each detector into the circuit. If Stim
                # doesn't find non-determinism, then this detector can be used
                # in the actual main circuit we're compiling. If not, can't.
                for detector in code.detector_schedule[relative_round]:
                    assert detector.lid_end == relative_round
                    if detector.has_open_floor(0, layer, code.schedule_length):
                        # This detector should become a 'lid-only' detector in
                        # this layer, unless it's non-deterministic.
                        lid_only = Stabilizer(detector.lid, relative_round)
                        if self.is_deterministic(lid_only, circuit, round):
                            layer_detector_schedule[relative_round].append(lid_only)
                    elif detector.floor_start + shift >= 0:
                        # This detector is always going to be comparing a floor
                        # with a lid, so should always be deterministic.
                        layer_detector_schedule[relative_round].append(detector)
                    # In all other cases, build this detector for the first
                    # time in the next layer.

                    # Remove this detector from the little test circuit so that in
                    # the next run of this for loop Stim is only considering the
                    # next detector.
                    circuit.measurer.reset_triggers()

                # Increase the tick before the next round
                tick += 2

            # Increase the layer and find the minmum floor start round in the
            # next layer. If all floors start at a non-negative round, then
            # we're done with this special initialisation logic.
            layer += 1
            min_floor_start += code.schedule_length
            done = min_floor_start >= 0

        return layer, layer_detector_schedules

    def product_measurement_targets(self, check: Check, circuit: Circuit):
        assert len(check.paulis) > 0
        product = PauliProduct(check.paulis)
        assert product.word.sign in [1, -1]
        # Do first pauli separately, then do the rest in a for loop.
        pauli = check.paulis[0]
        targeter = self.stim_pauli_targeters[pauli.letter.letter]
        invert = product.word.sign == -1
        # If inverting, it applies to the whole product, but equivalently can
        # just invert one qubit - may as well pick the first one.
        targets = [targeter(circuit.qubit_index(pauli.qubit), invert)]
        for pauli in check.paulis[1:]:
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
            self, stabilizer: Stabilizer, circuit: Circuit, round: int):
        circuit.measurer.add_detectors([stabilizer], round)
        stim_circuit = circuit.to_stim(NoNoise())
        try:
            stim_circuit.detector_error_model(
                approximate_disjoint_errors=True)
            # TODO - assert there's only one detector in this circuit.
            return True
        except ValueError as error:
            if 'circuit contains non-deterministic detectors' in str(error):
                return False
            else:
                # Pass it on!
                raise error


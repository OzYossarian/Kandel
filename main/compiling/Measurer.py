from collections import defaultdict
from typing import List

import stim

from main.building_blocks.Check import Check
from main.building_blocks.Detector import Detector
from main.compiling.Instruction import Instruction


class Measurer:
    def __init__(self):
        """ A separate class for handling measurement logic in stim circuits.
        Stim assigns numbers to each measurement, which are then used when
        building detectors and measuring logical operators. This class tracks
        all of this. A Measurer should be associated to a single circuit -
        e.g. can't use the same Measurer across several circuits.
        """
        # Note total number of measurements made. Used for calculating stim
        # measurement 'targets'.
        self.total_measurements = 0

        # Note which instructions correspond to the measurement of which
        # checks and in which rounds. Keys are Instructions, values are
        # (check, round, relative_round) pairs.
        self.measurement_checks = {}
        # Track the numbers stim assigns to the measurement of a given check
        # in a given round. Keys are (check, round) pairs.
        self.measurement_numbers = {}

        # Map observables to their index in stim.
        self.observable_indexes = {}

        # A measurement can lead to a detector being built, so we should track
        # which measurements trigger what.

        # Keys of 'detectors_triggered' are (check, relative_round) pairs, and
        # values are sets of detectors.
        self.detectors_triggered = defaultdict(set)
        # Keys of 'detector_triggers' are detectors, and values are sets
        # of (check, relative_round) pairs
        self.detector_triggers = defaultdict(set)

    def add_measurement(
            self, measurement: Instruction, check: Check, round: int,
            relative_round: int):
        self.measurement_checks[measurement] = (check, round, relative_round)

    def add_detectors(self, detector_schedule: List[List[Detector]]):
        for relative_round, detectors in enumerate(detector_schedule):
            for detector in detectors:
                for (t, check) in detector.lid:
                    if t == 0:
                        self.detectors_triggered[(check, relative_round)]\
                            .add(detector)
                        self.detector_triggers[detector]\
                            .add((check, relative_round))

    # def add_observable_update(
    #         self, checks: List[Check], round: int):
    #     dependencies = [(check, round) for check in checks]
    #     for check in checks:
    #         self.observable_updates[(check, round)] = dependencies

    def measurements_to_stim(self, measurements: List[Instruction]):
        detectors = []
        for measurement in measurements:
            # First record the measurement numbers
            check, round, relative_round = self.measurement_checks[measurement]
            self.measurement_numbers[(check, round)] = self.total_measurements
            self.total_measurements += 1

            # Now check if any detectors can be built as a result.
            for detector in self.detectors_triggered[(check, relative_round)]:
                # If this check (amongst others) triggers a detector,
                # note this down.
                triggers = self.detector_triggers[detector]
                can_build_detector = all([
                    (check, round) in self.measurement_numbers
                    for check, _ in triggers])
                if can_build_detector:
                    # All triggers measured - can now compile this detector!
                    # (Or at the very least, its lid). But must wait til all
                    # measurement numbers have been assigned before turning
                    # this detector into a stim instruction.
                    # TODO - this might actually be a bit wrong - the triggers
                    #  should probably actually be the whole lid, not just the
                    #  final checks measured. But because of how
                    #  'get_detector_targets' works this doesn't actually
                    #  cause problems at the minute.
                    detectors.append((detector, round))

        # Now turn detectors into stim instructions.
        instructions = []
        for detector, round in detectors:
            targets = self.get_detector_targets(detector, round)
            instructions.append(stim.CircuitInstruction('DETECTOR', targets))

        return instructions

    def get_detector_targets(self, detector: Detector, current_round: int):
        targets = []

        def get_face_targets(face):
            # Find the actual rounds in which the checks that constitute the
            # detector face were measured
            face = [
                (current_round + rounds_ago, check)
                for rounds_ago, check in face]
            # Only if every check in this face has been measured can we build
            # the detector face.
            if all([round >= 0 for round, check in face]):
                # Find the 'target' that stim will have assigned each check
                face_targets = [
                    self.measurement_target(check, round)
                    for round, check in face]
                return face_targets
            else:
                return []

        targets.extend(get_face_targets(detector.lid))
        targets.extend(get_face_targets(detector.floor))
        return targets

    def measurement_target(self, check: Check, round: int):
        measurements_ago = \
            self.measurement_numbers[(check, round)] - \
            self.total_measurements
        return stim.target_rec(measurements_ago)

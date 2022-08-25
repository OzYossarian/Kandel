from collections import defaultdict
from typing import List, Iterable, Tuple

import stim

from main.building_blocks.Check import Check
from main.building_blocks.detectors.Detector import Detector
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.compiling.Instruction import Instruction
from main.utils.types import Coordinates


class Measurer:
    def __init__(self):
        """A separate class for handling measurement logic in stim circuits.
        Stim assigns numbers to each measurement, which are then used when
        building detectors and measuring logical operators. This class tracks
        all of this. A Measurer should be associated to a single circuit -
        e.g. can't use the same Measurer across several circuits.

        A key point: just because measurements occur in the same round in
        the abstract definition of the code, this does NOT mean they will
        occur in the same tick in the circuit - e.g. because syndrome
        extraction circuits for different Paulis can have different lengths.
        This is why we do things in what might seem initially to be a
        convoluted way - we note down which measurements correspond to which
        checks in which rounds, then later on, when actually compiling to a
        Stim circuit, we dig up this information again and built detectors
        and update observables accordingly.
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

        # Map observables to their index in Stim
        self.observable_indexes = {}

        # A measurement can lead to a detector being built or an observable
        # being updated - we track which measurements trigger what.
        # Keys are (check, round) pairs, and values are lists whose elements
        # are detectors or observables.
        self.triggers = defaultdict(list)
        # To prevent duplicate detectors being built, track those that we've
        # already made.
        self.detectors_built = defaultdict(bool)

    def add_measurement(self, measurement: Instruction, check: Check, round: int):
        self.measurement_checks[measurement] = (check, round)

    def add_detectors(self, detectors: Iterable[Detector], round: int):
        for detector in detectors:
            for check in detector.final_slice:
                self.triggers[(check, round)].append(detector)

    def add_to_logical_observable(
        self, checks: Iterable[Check], observable: LogicalOperator, round: int
    ):
        for check in checks:
            self.triggers[(check, round)].append(observable)

    def measurements_to_stim(
        self, measurements: List[Instruction], shift_coords: Tuple[Coordinates] | None
    ):
        # Measurements can potentially trigger detectors being built or
        # observables being updated.
        detectors = []
        observable_updates = defaultdict(list)
        track_coords = shift_coords is not None

        for measurement in measurements:
            # First record the measurement numbers
            check, round = self.measurement_checks[measurement]
            self.measurement_numbers[(check, round)] = self.total_measurements
            self.total_measurements += 1

            # Now see if measuring this check triggers any extra instructions.
            for trigger in self.triggers[(check, round)]:
                if isinstance(trigger, Detector):
                    # This check (amongst others) triggers a detector.
                    detector = trigger
                    if self.can_build_detector(detector, round):
                        # Must wait til all measurement numbers have been
                        # assigned (at the end of the outer for loop we're in)
                        # before turning this detector into a Stim instruction
                        detectors.append((detector, round))
                else:
                    # Must be an observable update.
                    assert isinstance(trigger, LogicalOperator)
                    observable = trigger
                    # Again, must wait til all measurement numbers have been
                    # assigned before turning this into a Stim instruction.
                    observable_updates[observable].append((check, round))

        # Can now actually create corresponding Stim instructions.
        instructions = []
        for detector, round in detectors:
            instructions.append(self.detector_to_stim(detector, round, track_coords))
        for observable, checks in observable_updates.items():
            targets = [self.measurement_target(check, round) for check, round in checks]
            index = self.observable_index(observable)
            instructions.append(
                stim.CircuitInstruction("OBSERVABLE_INCLUDE", targets, [index])
            )

        return instructions

    def detector_to_stim(self, detector: Detector, round: int, track_coords: bool):
        targets = [
            self.measurement_target(check, round + rounds_ago)
            for rounds_ago, check in detector.timed_checks_mod_2]
        # Anchor needs to now be a tuple for Stim to accept it.
        if track_coords and isinstance(detector.anchor, tuple):
            anchor = detector.anchor
        elif track_coords:
            anchor = (detector.anchor,)
        else:
            anchor = ()
        return stim.CircuitInstruction("DETECTOR", targets, anchor)

    def can_build_detector(self, detector: Detector, round: int):
        # Only build this detector if all the checks in the final slice have
        # actually been measured, and if we haven't already built an
        # equivalent detector (one that compares the exact same measurements).
        final_slice_measured = all([
            (check, round) in self.measurement_numbers
            for check in detector.final_slice])
        if final_slice_measured:
            # First criteria met...
            measurement_numbers = tuple(sorted([
                self.measurement_numbers[(check, round + rounds_ago)]
                for rounds_ago, check in detector.timed_checks_mod_2]))

            already_built = self.detectors_built[measurement_numbers]
            if not already_built:
                # Second criteria met - can build this detector!
                # Update the detectors_built dictionary while we have the
                # measurement numbers to hand.
                self.detectors_built[measurement_numbers] = True
                return True
        return False

    def measurement_target(self, check: Check, round: int):
        measurements_ago = (
            self.measurement_numbers[(check, round)] - self.total_measurements
        )
        return stim.target_rec(measurements_ago)

    def observable_index(self, observable: LogicalOperator):
        # Get the stim index corresponding to this observable, or create one
        # if it doesn't yet have one.
        if observable in self.observable_indexes:
            index = self.observable_indexes[observable]
        else:
            index = len(self.observable_indexes)
            self.observable_indexes[observable] = index
        return index


    def reset_compilation(self):
        """
        """
        self.measurement_numbers = {}
        self.detectors_built = defaultdict(bool)
        self.total_measurements = 0

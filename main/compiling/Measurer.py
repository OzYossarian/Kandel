from collections import defaultdict
from typing import List, Iterable, Tuple, Dict, Union

import stim

from main.building_blocks.Check import Check
from main.building_blocks.detectors.Detector import Detector
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.compiling.Instruction import Instruction
from main.utils.types import Coordinates


Trigger = Union[Detector, LogicalOperator]


class Measurer:
    def __init__(self):
        """A separate class for handling measurement logic in stim circuits.
        Stim assigns numbers to each measurement, which are then used when
        compiling detectors and measuring logical operators. This class tracks
        all of this. A Measurer should be associated to a single circuit -
        e.g. can't use the same Measurer across several circuits.

        A key point: just because measurements occur in the same round in
        the abstract definition of the code, this does NOT mean they will
        occur in the same tick in the circuit - e.g. because syndrome
        extraction circuits for different Paulis can have different lengths.
        This is why we do things in what might seem initially to be a
        convoluted way - we note down which measurements correspond to which
        checks in which rounds, then later on, when actually compiling to a
        Stim circuit, we dig up this information again and compile detectors
        and update observables accordingly.
        """
        # Note total number of measurements made. Used for calculating stim
        # measurement 'targets'.
        self.total_measurements = 0

        # Note which instructions correspond to the measurement of which
        # checks and in which rounds. Keys are Instructions, values are
        # (check, round) pairs.
        self.measurement_checks: Dict[Instruction, Tuple[Check, int]] = {}
        # Track the numbers stim assigns to the measurement of a given check
        # in a given round. Keys are (check, round) pairs.
        self.measurement_numbers: Dict[Tuple[Check, int], int] = {}

        # Map observables to their index in Stim
        self._observable_indexes = {}

        # A measurement can lead to a detector being compiled or an observable
        # being updated - we track which measurements trigger what.
        # Keys are (check, round) pairs, and values are lists whose elements
        # are detectors or observables.
        self.triggers: Dict[Tuple[Check, int], List[Trigger]] = \
            defaultdict(list)
        # To prevent duplicate detectors being compiled, track those that we've
        # already made.
        self.detectors_compiled: Dict[Tuple[int], bool] = defaultdict(bool)

    def add_measurement(self, measurement: Instruction, check: Check, round: int):
        self.measurement_checks[measurement] = (check, round)

    def add_detectors(self, detectors: Iterable[Detector], round: int):
        for detector in detectors:
            for check in detector.final_checks:
                self.triggers[(check, round)].append(detector)

    def multiply_observable(
        self, checks: Iterable[Check], observable: LogicalOperator, round: int
    ):
        for check in checks:
            self.triggers[(check, round)].append(observable)

    def measurement_triggers_to_stim(
        self, measurements: List[Instruction], shift_coords: Union[Tuple[Coordinates], None]
    ):
        # TODO - have just realised that everything triggered by measurements
        #  (detectors, observable updates, shift coords) can probably all be
        #  Instructions, which would simplify things a bit. The reason I wrote
        #  it the way it is now is because I wanted these things to cope with
        #  circuit compression - e.g. if a detector consists of a set of
        #  measurements, but some measurements are moved to different ticks
        #  during compression, I wanted the detector to still compile
        #  correctly. But I think this can still be done if these triggers
        #  are Instructions.
        # Measurements can potentially trigger detectors being compiled or
        # observables being updated.
        detectors = []
        observable_multipliers = defaultdict(list)
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
                    if self.can_compile_detector(detector, round):
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
                    observable_multipliers[observable].append((check, round))

        # Can now actually create corresponding Stim instructions.
        instructions = []
        for detector, round in detectors:
            instructions.append(self.detector_to_stim(
                detector, round, track_coords))
        for observable, checks in observable_multipliers.items():
            targets = [self.measurement_target(
                check, round) for check, round in checks]
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

    def can_compile_detector(self, detector: Detector, round: int):
        # Only compile this detector if all the final checks have
        # actually been measured, and if we haven't already compiled an
        # equivalent detector (one that compares the exact same measurements).

        final_checks_measured = all([
            (check, round) in self.measurement_numbers
            for check in detector.final_checks])

        if final_checks_measured:
            # First criteria met...
            measurement_numbers = tuple(sorted([
                self.measurement_numbers[(check, round + rounds_ago)]
                for rounds_ago, check in detector.timed_checks_mod_2]))
            already_compiled = self.detectors_compiled[measurement_numbers]
            if not already_compiled:
                # Second criteria met - can compile this detector!
                self.detectors_compiled[measurement_numbers] = True
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
        if observable in self._observable_indexes:
            index = self._observable_indexes[observable]
        else:
            index = len(self._observable_indexes)
            self._observable_indexes[observable] = index
        return index

    def reset_compilation(self):
        """
        """
        self.measurement_numbers = {}
        self.detectors_compiled = defaultdict(bool)
        self.total_measurements = 0

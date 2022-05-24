from __future__ import annotations

from typing import Dict, Any, List, Set
from typing import TYPE_CHECKING

from main.building_blocks.Detector import Detector

if TYPE_CHECKING:
    from main.QPUs.QPU import QPU

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Coordinates, Qubit

CodeId = Any


class Code:
    def __init__(
            self, data_qubits: Dict[Coordinates, Qubit] | List[Qubit],
            schedule: List[List[Check]] = None,
            detectors: List[List[Detector]] = None):
        self.data_qubits = data_qubits
        # Declare attributes here but use separate method to set them.
        # Allows for a code to be partially instantiated but then for
        # schedule and detector to be set later.
        self.schedule: List[List[Check]] | None = None
        self.checks: Set[Check] | None = None
        self.detectors: List[List[Detector]] | None = None
        self.schedule_length: int | None = None
        if schedule:
            self.set_schedule_and_detectors(schedule, detectors)

        # TODO - add [n,k,d] parameters?

    def set_schedule_and_detectors(
            self, schedule: List[List[Check]],
            detectors: List[List[Detector]] = None):
        """Made this method separate so that it can be called after a call to
        super().__init__ in subclasses. See subclasses for why it's useful.
        """
        self.schedule = schedule
        self.schedule_length = len(schedule)
        self.checks = set(check for round in schedule for check in round)
        if len(self.schedule) == 1 and detectors is None:
            # Default case: each detector is made of one check measured
            # twice in consecutive rounds.
            self.detectors = [
                Detector([(-1, check)], [(0, check)])
                for check in self.schedule[0]]
        else:
            # If the length of the schedule is more than 1, force the user to
            # pass in the detectors - can't (yet?) automatically figure this
            # out.
            assert detectors is not None
            self.detectors = detectors

    def transform_coords(self, qpu: QPU):
        # A pre-processing step before embedding a code into a particular QPU.
        # Allows coordinates to be transformed to fit the particular geometry
        # of the given QPU. e.g.  Can be used to flatten a 3D layout onto a 2D
        # one, before actually doing the embedding into a QPU.
        pass

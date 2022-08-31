from __future__ import annotations

from collections import defaultdict
from typing import Dict, Any, List, Set
from typing import TYPE_CHECKING

from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.utils.types import Coordinates
from main.utils.utils import embed_coords

if TYPE_CHECKING:
    from main.QPUs.QPU import QPU

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit

CodeId = Any


class Code:
    def __init__(
            self, data_qubits: Dict[Coordinates, Qubit] | List[Qubit],
            check_schedule: List[List[Check]] = None,
            detector_schedule: List[List[Drum]] = None,
            logical_qubits: List[LogicalQubit] = None,
            distance: int = None):
        self.data_qubits = data_qubits
        self.distance = distance
        if logical_qubits is None:
            logical_qubits = []
        self.logical_qubits = logical_qubits

        # Assign the code a dimension based on data qubits' dimension.
        qubit_dims = {qubit.dimension for qubit in self.data_qubits.values()}
        self.dimension = max(qubit_dims)
        if len(qubit_dims) > 1:
            raise ValueError(
                f'All data qubits must have the same dimension! Set of all '
                f'qubit dimensions is instead {qubit_dims}.')

        # Compiler will set up ancilla qubits later if needed
        self.ancilla_qubits = {}

        # Declare attributes here but use separate method to set them.
        # Allows for a code to be partially instantiated but then for
        # schedule and detector to be set later.
        self.check_schedule: List[List[Check]] | None = None
        self.detector_schedule: List[List[Drum]] | None = None
        self.schedule_length: int | None = None
        self.checks: Set[Check] | None = None
        self.detectors: Set[Drum] | None = None

        if check_schedule:
            self.set_schedules(check_schedule, detector_schedule)

    def set_schedules(
            self, check_schedule: List[List[Check]],
            detector_schedule: List[List[Drum]] = None):
        # TODO - rethink whether this is the right abstraction/signature/thing
        #  - e.g. for subsystem codes, could do more than just force the user
        #  to define the whole detector schedule.
        self.check_schedule = check_schedule
        self.schedule_length = len(check_schedule)
        self.checks = set(
            check for round in check_schedule for check in round)

        if len(self.check_schedule) == 1 and detector_schedule is None:
            # Default case: each detector is made of one check measured
            # twice in consecutive rounds.
            self.detector_schedule = [[]]
            for check in self.check_schedule[0]:
                anchor = embed_coords(check.anchor, check.dimension + 1) \
                    if check.anchor is not None \
                    else None
                drum = Drum([(-1, check)], [(0, check)], 0, anchor)
                self.detector_schedule[0].append(drum)
        else:
            # If the length of the schedule is more than 1, force the user to
            # pass in the detectors - can't (yet?) automatically figure this
            # out.
            assert detector_schedule is not None
            assert self.schedule_length == len(detector_schedule)
            self.detector_schedule = detector_schedule

        self.detectors = set(
            detector
            for round in self.detector_schedule
            for detector in round)

    def update_logical_qubits(
            self, round: int) -> Dict[LogicalOperator, List[Check]]:
        # Should update the operators of the logical qubits, and return all
        # the checks that were multiplied into the operator to perform this
        # update.
        return defaultdict(list)

    def transform_coords(self, qpu: QPU):
        # A pre-processing step before embedding a code into a particular QPU.
        # Allows coordinates to be transformed to fit the particular geometry
        # of the given QPU. e.g.  Can be used to flatten a 3D layout onto a 2D
        # one, before actually doing the embedding into a QPU.
        pass

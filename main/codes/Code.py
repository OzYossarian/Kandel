from __future__ import annotations

from typing import Dict, Any, List, Set
from typing import TYPE_CHECKING

from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.utils.types import Coordinates
from main.utils.utils import embed_coords

if TYPE_CHECKING:
    from main.QPUs.QPU import QPU

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit

CodeId = Any


class Code:
    """
    Base class for all quantum error correction codes.
    """
    def __init__(
            self, data_qubits: Dict[Coordinates, Qubit] | List[Qubit],
            check_schedule: List[List[Check]] = None,
            detector_schedule: List[List[Drum]] = None,
            logical_qubits: List[LogicalQubit] = None,
            distance: int = None):
        """
        Args:
            data_qubits:
                The data qubits within this code. Can be given either as a
                dictionary keyed by coordinates, or as a list (the latter will
                be converted to a dictionary keyed by integers).
            check_schedule:
                The checks that are measured at each round of the code.
                That is, element i of this parameter should be the list of
                checks measured at round i.
                    Can be left as None initially, and then set later via the
                `set_schedules` method.
            detector_schedule:
                The detectors built at the end of each round of the code.
                That is, element i of this parameter should be the list of
                detectors built immediately after round i.
                    Can be left as None initially, and then set later via the
                `set_schedules` method. If left as None, and `check_schedule`
                has length 1, then we assume this is a stabilizer code and
                auto-build the detectors.
            logical_qubits:
                The logical qubits of the code. If any of these are not of
                interest, they can be left as None. Then defaults to the
                empty list.
            distance:
                The distance of the code. If this isn't of interest, it can
                be left as None.
        """
        if isinstance(data_qubits, list):
            # Convert to a dictionary.
            data_qubits = {
                i: data_qubit for i, data_qubit in enumerate(data_qubits)}
        self._assert_data_qubits_valid(data_qubits)

        if logical_qubits is None:
            logical_qubits = []

        self.data_qubits = data_qubits
        self.distance = distance
        self.logical_qubits = logical_qubits

        # Compiler will set up ancilla qubits later if needed
        self.ancilla_qubits = {}

        # Declare attributes here but use separate method to set them.
        # Allows for a code to be partially instantiated (e.g. in order to
        # create the data qubits) but then for the code and detector
        # schedules to be set later.
        self.check_schedule: List[List[Check]] | None = None
        self.detector_schedule: List[List[Drum]] | None = None
        self.schedule_length: int | None = None
        self.checks: Set[Check] = set()
        self.detectors: Set[Drum] = set()

        if check_schedule:
            self.set_schedules(check_schedule, detector_schedule)

    def set_schedules(
            self, check_schedule: List[List[Check]],
            detector_schedule: List[List[Drum]] = None):
        """
        Set the code's check schedule and detector schedule.
        TODO - this design (calling this method later after partially
         instantiating a Code) just feels awkward and clumsy. Can't think
         of anything better though! Keep pondering.

        Args:
            check_schedule:
                The checks that are measured at each round of the code.
                That is, element i of this parameter should be the list of
                checks measured at round i.
            detector_schedule:
                The detectors built at the end of each round of the code.
                That is, element i of this parameter should be the list of
                detectors built immediately after round i.
                    If left as None, and `check_schedule` has length 1,
                then we assume this is a stabilizer code and auto-build the
                detectors.
        """
        self._assert_check_schedule_valid(check_schedule)

        self.check_schedule = check_schedule
        self.schedule_length = len(check_schedule)
        # Also save all checks in an unstructured set, for convenience.
        self.checks = set(
            check
            for round in check_schedule
            for check in round)

        if len(self.check_schedule) == 1 and detector_schedule is None:
            # Default case: stabilizer code! Each detector is made of one
            # check measured twice in consecutive rounds.
            self.detector_schedule = [[]]
            for check in self.check_schedule[0]:
                # We give Detectors spacetime coordinates, hence embedding them
                # in one dimension higher.
                anchor = embed_coords(check.anchor, check.dimension + 1) \
                    if check.anchor is not None \
                    else None
                drum = Drum([(-1, check)], [(0, check)], 0, anchor)
                self.detector_schedule[0].append(drum)
        else:
            # If the length of the schedule is more than 1, force the user to
            # manually define the detectors.
            # TODO - is there a neater abstraction for this? e.g. perhaps for
            #  subsystem codes we can do more than just force the user to
            #  pass in the whole detector schedule?
            self._assert_detector_schedule_valid(detector_schedule)
            self.detector_schedule = detector_schedule

        # Also save all detectors in an unstructured set, for convenience.
        self.detectors = set(
            detector
            for round in self.detector_schedule
            for detector in round)

    @property
    def dimension(self) -> int:
        # Just echo the data qubits' dimension; we already check that these
        # dimensions are valid, and that we have at least one data qubit.
        return list(self.data_qubits.values())[0].dimension

    @staticmethod
    def _assert_data_qubits_valid(data_qubits: Dict[Coordinates, Qubit]):
        if len(data_qubits) == 0:
            raise ValueError(f"Can't make a code without any data qubits!")
        qubit_dims = {qubit.dimension for qubit in data_qubits.values()}
        if len(qubit_dims) > 1:
            raise ValueError(
                f'Data qubits in a code must all have the same dimensions! '
                f'Set of all qubit dimensions is instead {qubit_dims}. '
                f'Given data qubits are {list(data_qubits.values())}')
        all_tuples = all([
            qubit.has_tuple_coords for qubit in data_qubits.values()])
        all_non_tuples = all([
            not qubit.has_tuple_coords for qubit in data_qubits.values()])
        if not (all_tuples or all_non_tuples):
            raise ValueError(
                "Data qubits in a code must either all have tuple "
                "coordinates or all have non-tuple coordinates. "
                f"Given data qubits are {list(data_qubits.values())}")
        unique_data_qubits = {qubit for qubit in data_qubits.values()}
        coords = {qubit.coords for qubit in unique_data_qubits}
        if len(coords) != len(unique_data_qubits):
            raise ValueError(
                f"Data qubits in a code must all have unique coordinates! "
                f"Instead, found {len(unique_data_qubits)} data qubits, "
                f"but only {len(coords)} unique coordinates. "
                f"Given data qubits are {list(data_qubits.values())}")

    def _assert_check_schedule_valid(self, check_schedule: List[List[Check]]):
        if len(check_schedule) == 0:
            raise ValueError("Check schedule must have at least one round!")
        qubits = {
            pauli.qubit
            for round in check_schedule
            for check in round
            for pauli in check.paulis.values()}
        if not qubits.issubset(self.data_qubits.values()):
            raise ValueError(
                "Checks within a code should only involve that code's "
                f"data qubits! Check schedule is {check_schedule}, "
                f"and data qubits are {list(self.data_qubits.values())}.")

    def _assert_detector_schedule_valid(
            self, detector_schedule: List[List[Drum]]):
        if detector_schedule is None:
            raise ValueError(
                "Can't auto-create a detector schedule for a check "
                "schedule with more than one round. Instead, a detector "
                "schedule must be supplied manually. "
                f"Check schedule is {self.check_schedule}.")
        if self.schedule_length != len(detector_schedule):
            raise ValueError(
                f"Detector schedule length must be the same as the check "
                f"schedule length! Here we have {len(detector_schedule)} "
                f"and {self.schedule_length} respectively. "
                f"Check schedule is {self.check_schedule}, while "
                f"detector schedule is {detector_schedule}")
        detector_checks = {
            check
            for round in detector_schedule
            for detector in round
            for _, check in detector.timed_checks}
        if not detector_checks.issubset(self.checks):
            raise ValueError(
                "Detectors within a code should only involve checks in "
                f"the code's check schedule! "
                f"Detector schedule is {detector_schedule}, and "
                f"check schedule is {self.check_schedule}.")

    def transform_coords(self, qpu: QPU):
        # A pre-processing step before embedding a code into a particular QPU.
        # Allows coordinates to be transformed to fit the particular geometry
        # of the given QPU. e.g.  Can be used to flatten a 3D layout onto a 2D
        # one, before actually doing the embedding into a QPU.
        pass

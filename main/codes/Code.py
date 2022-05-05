from __future__ import annotations

from typing import Dict, Any, List
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main.QPUs.QPU import QPU

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Coordinates, Qubit

CodeId = Any


class Code:
    def __init__(
            self, data_qubits: Dict[Coordinates, Qubit],
            schedule: List[List[Check]],
            ancilla_qubits: Dict[Coordinates, Qubit] = None):
        self.data_qubits = data_qubits
        # Declare schedule and checks here but use separate method to set them
        self.schedule = None
        self.checks = None
        self.set_schedule(schedule)

        # TODO - ideally, code shouldn't care about ancillas - these have no
        #  place in the mathematical definition of a code, so are just
        #  implementation details. Compiler should handle, perhaps.
        self.ancilla_qubits = ancilla_qubits
        # TODO - add [n,k,d] parameters?

    def set_schedule(self, schedule: List[List[Check]]):
        """Made this method separate so that it can be called after a call to
        super().__init__ in subclasses. See subclasses for why it's useful.
        """
        self.schedule = schedule
        self.checks = set(check for round in schedule for check in round)

    def transform_coords(self, qpu: QPU):
        # A pre-processing step before embedding a code into a particular QPU.
        # Allows coordinates to be transformed to fit the particular geometry
        # of the given QPU. e.g.  Can be used to flatten a 3D layout onto a 2D
        # one, before actually doing the embedding into a QPU.
        pass

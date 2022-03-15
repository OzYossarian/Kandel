from __future__ import annotations

from typing import Dict, Any, List, Iterable
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main.QPUs.QPU import QPU

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Coordinates, Qubit

CodeId = Any


class Code:
    def __init__(self, data_qubits: Dict[Coordinates, type(Qubit)],
                 schedule: List[Iterable[type(Check)]]):
        self.data_qubits = data_qubits
        self.schedule = schedule
        self.checks = set(check for round in schedule for check in round)

    def transform_coords(self, qpu: QPU):
        # A pre-processing step before embedding a code into a particular QPU.
        # Allows coordinates to be transformed to fit the particular geometry
        # of the given QPU.
        pass

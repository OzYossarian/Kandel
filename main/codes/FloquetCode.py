from typing import Dict, List, Iterable

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Coordinates, Qubit
from main.codes.Code import Code


class FloquetCode(Code):
    def __init__(self, data_qubits: Dict[Coordinates, type(Qubit)],
                 schedule: List[Iterable[type(Check)]]):
        assert len(schedule) > 1  # Defining feature of a Floquet code
        super().__init__(data_qubits, schedule)

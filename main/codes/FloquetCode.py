from typing import Dict, List, Iterable

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Coordinates, Qubit
from main.codes.Code import Code


class FloquetCode(Code):
    def __init__(self, data_qubits: Dict[Coordinates, Qubit],
                 schedule: List[List[Check]]):
        super().__init__(data_qubits, schedule)

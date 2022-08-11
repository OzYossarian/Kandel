from typing import Dict

from main.codes.Code import Code, CodeId
from main.building_blocks.Qubit import Qubit
from main.utils.types import Coordinates


class QPU:
    def __init__(self, qubits: Dict[Coordinates, Qubit]):
        self.qubits = qubits
        self.codes: Dict[CodeId, Code] = {}

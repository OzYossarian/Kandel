from typing import Dict, Any, List, Iterable
from main.Check import Check
from main.Qubit import Coordinates, Qubit

CodeId = Any


class Code:
    def __init__(self, data_qubits: Dict[Coordinates, type(Qubit)],
                 schedule: List[Iterable[type(Check)]]):
        self.data_qubits = data_qubits
        self.schedule = schedule
        # add [n,k,d] parameters?

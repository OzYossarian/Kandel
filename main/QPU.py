import itertools
from typing import Tuple, Dict, Iterable

from main.Code import Code, CodeId
from main.Qubit import Qubit, State, Coordinates


class QPU:
    def __init__(self, qubits: Dict[Coordinates, Qubit], codes: Dict[CodeId, Code]):
        self.qubits = qubits
        self.codes = codes


class SquareLatticeQPU(QPU):
    def __init__(self, dims: Tuple[int, ...]):
        self.dims = dims
        self.dim = len(dims)
        positions = itertools.product(*(range(dim) for dim in dims))
        qubits = {position: Qubit(position, State.Zero) for position in positions}
        super().__init__(qubits, {})

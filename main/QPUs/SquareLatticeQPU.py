import itertools
from typing import Tuple

from main.QPUs.QPU import QPU
from main.building_blocks.Qubit import Qubit, Coordinates
from main.codes.Code import Code
from main.enums import State


class SquareLatticeQPU(QPU):
    def __init__(self, dims: Tuple[int, ...]):
        self.dims = dims
        self.dim = len(dims)
        if self.dim == 1:
            positions = range(dims[0])
        else:
            positions = itertools.product(*(range(dim) for dim in dims))
        qubits = {position: Qubit(position, State.Zero) for position in positions}
        super().__init__(qubits)

    def embed(self, code: Code, start: Coordinates, hyperplane: Coordinates):
        code.transform_coords(self)

        def embed_coords(coords: Coordinates):
            if self.dim == 1:
                # Must be embedding a 1D code into this 1D computer
                return coords + start
            else:
                embedded = list(start)
                if isinstance(coords, int):
                    # Must be embedding a 1D code into this higher dim QPU
                    embedded[hyperplane] += coords
                else:
                    for i in range(len(coords)):
                        embedded[hyperplane[i]] += coords[i]
                return tuple(embedded)

        for qubit in code.data_qubits.values():
            qubit.coords = embed_coords(qubit.coords)
            if qubit.coords not in self.qubits:
                raise ValueError(f"Can't embed a qubit at {qubit.coords} - "
                                 f"there's no qubit defined here on the QPU!")
            self.qubits[qubit.coords] = qubit

        for check in code.checks:
            check.center = embed_coords(check.center)

        code_id = len(self.codes) + 1
        self.codes[code_id] = code

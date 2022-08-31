import itertools
from typing import Tuple

from main.QPUs.QPU import QPU
from main.building_blocks.Qubit import Qubit
from main.codes.Code import Code
from main.utils.types import Coordinates
from main.utils.utils import coords_length


class SquareLatticeQPU(QPU):
    def __init__(self, dims: Tuple[int, ...] | int):
        self.dim = coords_length(dims)
        if self.dim == 1 and isinstance(dims, tuple):
            # Don't bother with a one-element tuple - turn it into an int.
            dims = dims[0]
        self.dims = dims
        if self.dim == 1:
            coords = range(dims)
        else:
            coords = itertools.product(*(range(dim) for dim in dims))
        qubits = {coords: Qubit(coords) for coords in coords}
        super().__init__(qubits)

    def embed(self, code: Code, start: Coordinates, hyperplane: Coordinates):
        code.transform_coords(self)

        def embed_coords(coords: Coordinates):
            if self.dim == 1:
                # Must be embedding a 1D code into this 1D computer. So
                # `coords` and `start` must both be ints.
                return coords + start
            else:
                # `start` should be a tuple instead
                embedded = list(start)
                if isinstance(coords, int):
                    # Must be embedding a 1D code into this higher dim QPU.
                    # So `hyperplane` and `coords` should both be ints.
                    embedded[hyperplane] += coords
                else:
                    # `hyperplane` and `coords` should both be tuples.
                    for i in range(len(coords)):
                        embedded[hyperplane[i]] += coords[i]
                return tuple(embedded)

        for qubit in code.data_qubits.values():
            qubit.coords = embed_coords(qubit.coords)
            if qubit.coords not in self.qubits:
                raise ValueError(
                    f"Can't embed a qubit at {qubit.coords} - there's no "
                    f"qubit defined here on the QPU!")
            self.qubits[qubit.coords] = qubit

        for check in code.checks:
            check.anchor = embed_coords(check.anchor)

        code_id = len(self.codes) + 1
        self.codes[code_id] = code

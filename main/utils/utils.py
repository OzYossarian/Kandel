from collections import defaultdict
from functools import reduce
from statistics import mean
from typing import List, Tuple, Hashable, Iterable
from pathlib import Path

from main.building_blocks.Qubit import Coordinates
from main.building_blocks.pauli.Pauli import Pauli


def output_path() -> Path:
    root = Path(__file__).parent.parent.parent
    output = Path(root, 'output')
    return output


def mid(coords: Iterable[Coordinates]) -> Coordinates:
    if all(isinstance(coord, tuple) for coord in coords):
        return tuple(map(mean, zip(*coords)))
    else:
        return mean(coords)


def xor(a: bool, b: bool) -> bool:
    return a != b


def modulo_duplicates(xs: List[Hashable], n: int):
    # As order-preserving as possible, given that we're removing elements.
    result: type(xs) = [None for _ in xs]
    indexes = defaultdict(list)
    for i, x in enumerate(xs):
        indexes[x].append(i)
    for x in xs:
        count = len(indexes[x])
        keep = indexes[x][:(count % n)]
        for k in keep:
            result[k] = xs[k]
    return [r for r in result if r is not None]

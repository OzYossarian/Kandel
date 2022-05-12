from collections import defaultdict
from statistics import mean
from typing import List, Tuple, Hashable
from pathlib import Path


def output_path() -> Path:
    root = Path(__file__).parent.parent
    output = Path(root, 'output')
    return output


def mid(a: Tuple[int, ...], b: Tuple[int, ...]) -> Tuple[int | float, ...]:
    return tuple(map(mean, zip(a, b)))


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



from statistics import mean
from typing import Tuple


def mid(a: Tuple[int, ...], b: Tuple[int, ...]):
    return tuple(map(mean, zip(a, b)))

from numbers import Number
from statistics import mean
from typing import Tuple
from pathlib import Path


class DebugFriendly:
    def __repr__(self):
        return str(vars(self))


def output_path() -> Path:
    root = Path(__file__).parent.parent
    output = Path(root, 'output')
    return output


def mid(a: Tuple[int, ...], b: Tuple[int, ...]) -> Tuple[Number, ...]:
    return tuple(map(mean, zip(a, b)))


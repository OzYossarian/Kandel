from collections import defaultdict
from functools import reduce
from statistics import mean
from typing import List, Tuple, Hashable, Iterable
from pathlib import Path

from main.building_blocks.pauli.Pauli import Pauli


def output_path() -> Path:
    root = Path(__file__).parent.parent.parent
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


def pauli_composition(paulis: Iterable[Pauli]):
    # Order matters because Pauli multiplication is not commutative.
    # We assume 'paulis' is ordered such that the rightmost element is the
    # first to be applied, and the leftmost element is the last to be applied
    # (i.e. the order in which we ordinarily write Paulis algebraically).
    # If two Paulis act on different qubits, it doesn't matter which comes
    # first in the ordering.

    # Group by the qubit that the Paulis are applied to
    grouped_paulis = defaultdict(list)
    for pauli in paulis:
        grouped_paulis[pauli.qubit].append(pauli.letter)
    # Compose together the Paulis on each qubit.
    composed = {
        qubit: reduce(lambda x, y: x.compose(y), letters)
        for qubit, letters in grouped_paulis.items()}
    # Return these as Paulis again
    result = [Pauli(qubit, letter) for qubit, letter in composed.items()]
    return result





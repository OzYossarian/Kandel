from collections import defaultdict
from statistics import mean
from typing import List, Tuple, Hashable, Iterable
from pathlib import Path

from main.building_blocks.Qubit import Coordinates


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


def tuple_sum(*tuples: Tuple[int | float, ...]):
    return tuple(map(sum, zip(*tuples)))


def tuple_minus(xs: Tuple[int | float, ...], ys: Tuple[int | float, ...]) -> object:
    return tuple(map(lambda pair: pair[0]-pair[1], zip(xs, ys)))


def embed_coords(
        coords: Coordinates, dimension: int, offset: Coordinates = None,
        hyperplane: Tuple[int, ...] = None):
    # Embed coordinates into a strictly higher dimension.
    # 'hyperplane' lets user embed into specific axes - e.g. if embedding 2D
    # coordinates into 3D, and hyperplane is (0, 1), this embeds coords into
    # the XY plane. If instead it's (0, 2), this embeds into XZ plane.
    # Defaults to (0, 1, ..., current_dimension-1)
    # 'offset' shifts embedded coordinates by the given amount.
    # Defaults to (0, 0, ..., 0)
    assert dimension > 1
    if offset is None:
        offset = tuple(0 for _ in range(dimension))
    else:
        assert len(offset) == dimension

    # Get the current dimension of the coordinates.
    if isinstance(coords, tuple):
        current_dimension = len(coords)
    else:
        assert isinstance(coords, int | float)
        current_dimension = 1
    assert dimension > current_dimension

    if hyperplane is None:
        hyperplane = tuple(i for i in range(current_dimension))

    # Finally, embed these coordinates into the given (hyper)plane
    embedded = list(offset)
    for i in range(current_dimension):
        embedded[hyperplane[i]] = coords[i]

    return tuple(embedded)


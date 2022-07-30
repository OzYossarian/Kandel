from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import List, Tuple, Hashable, Iterable, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from main.building_blocks.Qubit import Coordinates


def output_path() -> Path:
    root = Path(__file__).parent.parent.parent
    output = Path(root, 'output')
    return output


def coords_mid(coords: Iterable[Coordinates]) -> Coordinates:
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


def coords_sum(*coords: Coordinates):
    if all(isinstance(coord, tuple) for coord in coords):
        return tuple(map(sum, zip(*coords)))
    else:
        return sum(coords)


def coords_minus(x: Coordinates, y: Coordinates):
    if all(isinstance(coords, tuple) for coords in [x, y]):
        return tuple(map(lambda pair: pair[0]-pair[1], zip(x, y)))
    else:
        return x-y


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
    current_dimension = coords_length(coords)
    assert dimension > current_dimension

    if hyperplane is None:
        hyperplane = tuple(i for i in range(current_dimension))

    if current_dimension == 1:
        coords = (coords, )

    # Finally, embed these coordinates into the given (hyper)plane
    embedded = list(offset)
    for i in range(current_dimension):
        embedded[hyperplane[i]] = coords[i]

    return tuple(embedded)


def coords_length(coords: Coordinates):
    return len(coords) if isinstance(coords, tuple) else 1

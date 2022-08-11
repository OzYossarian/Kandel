from collections import defaultdict
from statistics import mean
from typing import List, Tuple, Hashable
from pathlib import Path

from main.utils.types import Coordinates


def output_path() -> Path:
    # TODO - Can't use a helper method like this when Kandel becomes a proper
    #  package.
    root = Path(__file__).parent.parent.parent
    output = Path(root, 'output')
    return output


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


def xor(a: bool, b: bool) -> bool:
    return a != b


def coords_mid(*coords: Coordinates) -> Coordinates:
    lengths = {coords_length(coord) for coord in coords}
    if len(lengths) != 1:
        raise ValueError(
            f"Can't find the midpoint of coordinates of different lengths. "
            f"Coordinates are {list(coords)}.")
    if all([isinstance(coord, tuple) for coord in coords]):
        return tuple(map(mean, zip(*coords)))
    else:
        return mean(coords)


def coords_sum(*coords: Coordinates) -> Coordinates:
    lengths = {coords_length(coord) for coord in coords}
    if len(lengths) != 1:
        raise ValueError(
            f"Can't sum over coordinates of different lengths. "
            f"Coordinates are {list(coords)}.")
    if all([isinstance(coord, tuple) for coord in coords]):
        return tuple(map(sum, zip(*coords)))
    else:
        return sum(coords)


def coords_minus(xs: Coordinates, ys: Coordinates):
    lengths = {coords_length(xs), coords_length(ys)}
    if len(lengths) != 1:
        raise ValueError(
            f"Can't sum over coordinates of different lengths. "
            f"Coordinates are {(xs, ys)}.")
    if isinstance(xs, tuple) and isinstance(ys, tuple):
        return tuple(x-y for x, y in zip(xs, ys))
    else:
        return xs - ys


def embed_coords(
        coords: Coordinates, dimension: int, offset: Coordinates = None,
        hyperplane: int | Tuple[int, ...] = None):
    # Embed coordinates into a strictly higher dimension.
    # 'hyperplane' lets user embed into specific axes - e.g. if embedding 2D
    # coordinates into 3D, and hyperplane is (0, 1), this embeds coords into
    # the XY plane. If instead it's (0, 2), this embeds into XZ plane.
    # Defaults to (0, 1, ..., current_dimension-1)
    # 'offset' shifts embedded coordinates by the given amount.
    # Defaults to (0, 0, ..., 0)

    current_dimension = coords_length(coords)
    if dimension <= current_dimension:
        raise ValueError(
            f"Can't embed coordinates {coords} into dimension {dimension} - "
            f"dimension must be greater than that of the coordinates.")

    if offset is None:
        offset = tuple(0 for _ in range(dimension))
    elif len(offset) != dimension:
        raise ValueError(
            f"Can't embed coordinates {coords} into dimension {dimension} "
            f"with offset {offset}, because offset does not have dimension "
            f"{dimension}.")

    if hyperplane is None:
        if isinstance(coords, tuple):
            hyperplane = tuple(i for i in range(current_dimension))
        else:
            hyperplane = 0
    elif xor(isinstance(coords, tuple), isinstance(hyperplane, tuple)):
        raise ValueError(
            f"Can't embed coordinates {coords} into dimension {dimension} in"
            f"hyperplane {hyperplane}, because types of coordinates and "
            f"hyperplane don't match. They should either both be tuples, or "
            f"neither of them should be.")
    elif coords_length(hyperplane) != current_dimension:
        raise ValueError(
            f"Can't embed coordinates {coords} into dimension {dimension} in"
            f"hyperplane {hyperplane}, because dimensions of coordinates and "
            f"hyperplane don't match.")

    # Finally, embed these coordinates into the given (hyper)plane
    embedded = list(offset)
    if isinstance(coords, tuple):
        for i in range(current_dimension):
            embedded[hyperplane[i]] += coords[i]
    else:
        embedded[hyperplane] += coords
    return tuple(embedded)


def coords_length(coords: Coordinates):
    return len(coords) if isinstance(coords, tuple) else 1

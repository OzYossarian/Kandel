import random
from typing import Callable, List

import numpy as np

from main.utils.types import Coordinates
from main.utils.utils import xor
from tests.utils.utils_numbers import default_max_unique_sample_size, default_min_coord, default_max_coord


def coords_length(coords: Coordinates):
    return len(coords) if isinstance(coords, tuple) else 1


def check_arguments(
        num: int,
        unique: bool,
        int_coords: bool,
        tuple_coords: bool,
        dimension: int | None,
        max_dimension: int | None,
        min_coord: int | float,
        max_coord: int | float,
):
    # dimension_args = [dimension, max_dimension, tuple_coords]
    # # Must provide some info about dimensions!
    # assert not all([arg is None for arg in dimension_args])

    if not tuple_coords:
        # Non-tuple coordinates requested.
        assert dimension in [1, None]
        assert max_dimension in [1, None]
        # Set dimension to be 1 in case both `dimension` and `max_dimension`
        # are None - makes life easier for the rest of this function.
        dimension = 1
    else:
        # Tuple coordinates requested.
        # Can't have both `dimension` and `max_dimension` non-None, because
        # this is how we infer whether dimensions can vary or not.
        assert xor(dimension is None, max_dimension is None)
        dim_arg = dimension if dimension is not None else max_dimension
        assert dim_arg > 0

    if int_coords:
        assert isinstance(min_coord, int)
        assert isinstance(max_coord, int)
        if unique:
            dim_arg = dimension if dimension is not None else max_dimension
            assert num <= default_max_unique_sample_size(
                dim_arg, min_coord, max_coord)


def random_coordss(
        num: int,
        unique: bool = False,
        int_coords: bool = False,
        tuple_coords: bool = True,
        dimension: int = None,
        max_dimension: int = None,
        min_coord: int | float = default_min_coord,
        max_coord: int | float = default_max_coord,
):
    check_arguments(
        num,
        unique,
        int_coords,
        tuple_coords,
        dimension,
        max_dimension,
        min_coord,
        max_coord)

    if not tuple_coords:
        # Specifically requested non-tuple coords.
        dimension = 1

    if int_coords:
        def get_components(n: int):
            return random.choices(range(min_coord, max_coord), k=n)
    else:
        def get_components(n: int):
            return np.random.uniform(min_coord, max_coord, n)

    if tuple_coords:
        def get_coords(components: List[int | float]):
            return tuple(components)
    else:
        def get_coords(components: List[int | float]):
            return components[0]

    if not unique:
        return _random_non_unique_coords(
            num, dimension, max_dimension, get_components, get_coords)
    else:
        return _random_unique_coords(
            num, dimension, max_dimension, get_components, get_coords)


def _random_non_unique_coords(
        num: int,
        dimension: int,
        max_dimension: int,
        get_components: Callable[[int], List[int | float]],
        get_coords: Callable[[List[int | float]], Coordinates]
) -> List[Coordinates]:
    dimensions = [dimension for _ in range(num)] \
        if dimension is not None \
        else [random.randint(1, max_dimension) for _ in range(num)]
    # Generate all components randomly at once, then chunk them up into
    # coordinates.
    num_components = sum(dimensions)
    components = get_components(num_components)
    coordss = []
    processed = 0
    for d in dimensions:
        coords_components = components[processed: processed + d]
        coords = get_coords(coords_components)
        coordss.append(coords)
        processed += d
    return coordss


def _random_unique_coords(
        num: int,
        dimension: int,
        max_dimension: int,
        get_components: Callable[[int], List[int | float]],
        get_coords: Callable[[List[int | float]], Coordinates]
) -> List[Coordinates]:
    # Bit less efficient, but not too bad. We just keep generating coords
    # and see if they're different to all the others we've generated so far.
    coordss = set()
    for _ in range(num):
        found_unique_coords = False
        while not found_unique_coords:
            dim = dimension \
                if dimension is not None \
                else random.randint(1, max_dimension)
            coords_components = get_components(dim)
            coords = get_coords(coords_components)
            if coords not in coordss:
                found_unique_coords = True
                coordss.add(coords)
    return list(coordss)


def random_coords(
        int_coords: bool = False,
        tuple_coords: bool = True,
        dimension: int = None,
        min_coord: int | float = default_min_coord,
        max_coord: int | float = default_max_coord,
):
    coordss = random_coordss(
        num=1,
        int_coords=int_coords,
        tuple_coords=tuple_coords,
        dimension=dimension,
        min_coord=min_coord,
        max_coord=max_coord)
    coords = coordss[0]
    return coords

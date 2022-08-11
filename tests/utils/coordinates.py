import random
from typing import Callable

import numpy as np

from main.utils.types import Coordinates


def random_tuple_coords(dimension: int, min: float, max: float):
    # All floats
    return tuple(np.random.uniform(min, max, dimension))


def random_tuple_coords_int(dimension: int, min: int, max: int):
    # All ints
    return tuple(random.choices(range(min, max), k=dimension))


def random_non_tuple_coords(min: float, max: float):
    # A random float
    return random.uniform(min, max)


def random_non_tuple_coords_int(min: int, max: int):
    # A random int
    return random.randint(min, max)


def _unique_random_coords(
        num: int, get_random_coords: Callable[[], Coordinates]):
    result = set()
    for _ in range(num):
        found_unique_coords = False
        while not found_unique_coords:
            coords = get_random_coords()
            if coords not in result:
                found_unique_coords = True
                result.add(coords)
    return result


def unique_random_tuple_coords(
        num: int, dimension: int, min: float = -10, max: float = 10):
    def get_random_coords():
        return random_tuple_coords(dimension, min, max)
    return _unique_random_coords(num, get_random_coords)


def unique_random_tuple_coords_int(
        num: int, dimension: int, min: int = -10, max: int = 10):
    def get_random_coords():
        return random_tuple_coords_int(dimension, min, max)
    return _unique_random_coords(num, get_random_coords)


def unique_random_non_tuple_coords(
        num: int, min: float = -10, max: float = 10):
    def get_random_coords():
        return random_non_tuple_coords(min, max)
    return _unique_random_coords(num, get_random_coords)


def unique_random_non_tuple_coords_int(
        num: int, min: int = -10, max: int = 10):
    def get_random_coords():
        return random_non_tuple_coords_int(min, max)
    return _unique_random_coords(num, get_random_coords)

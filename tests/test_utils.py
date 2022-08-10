import random
import statistics
import pytest
from collections import Counter
from typing import Callable, Iterable

from main.building_blocks.Qubit import Coordinates
from main.utils.utils import modulo_duplicates, coords_mid
from tests.utils.numbers import random_int_or_float


def test_modulo_duplicates():
    # Construct some random list of integers, apply the 'mod duplicates'
    # method, and check it worked. Repeat several times.
    repeat = 100
    for i in range(repeat):
        list_range = random.randint(1, 100)
        list_size = random.randint(1, 100)
        xs = random.choices(range(0, list_range), k=list_size)
        unique = set(xs)
        x_counts = Counter(xs)
        for j in range(1, list_size):
            ys = modulo_duplicates(xs, j)
            y_counts = Counter(ys)
            assert all(
                y_counts[item] == (x_counts[item] % j)
                for item in unique)


def test_output_path():
    # No test needed here because this method will be binned eventually.
    # In future, if user doesn't provide absolute path then we'll just
    # put files in the folder they're currently running code from.
    assert True


def _test_coords_mid(
        create_coords: Callable[[], Coordinates],
        get_expected_mid: Callable[[Iterable[Coordinates]], Coordinates]):
    repeats = 100
    num_coords = random.randint(1, 100)
    for _ in range(repeats):
        coordss = [create_coords() for _ in range(num_coords)]
        mid = coords_mid(coordss)
        expected_mid = get_expected_mid(coordss)
        assert mid == expected_mid


def test_coords_mid_if_all_coords_tuples():
    coords_dim = random.randint(1, 100)
    coord_range = (-100, 100)

    def create_coords():
        # Randomly pick int or float for each coordinate
        return tuple([
            random_int_or_float(coord_range[0], coord_range[1])
            for _ in range(coords_dim)])

    def get_expected_mid(coordss: Iterable[Coordinates]):
        return tuple([
            statistics.mean([coords[d] for coords in coordss])
            for d in range(coords_dim)])

    _test_coords_mid(create_coords, get_expected_mid)


def test_coords_mid_if_all_coords_singletons():
    coord_range = (-100, 100)

    def create_coords():
        return random_int_or_float(coord_range[0], coord_range[1])

    def get_expected_mid(coordss: Iterable[Coordinates]):
        return statistics.mean(coordss)

    _test_coords_mid(create_coords, get_expected_mid)


def test_coords_mid_fails_if_lengths_unequal():
    coords = [0, (1, 1)]
    with pytest.raises(ValueError):
        coords_mid(coords)

    coords = [(0, 0), (1, 1, 1)]
    with pytest.raises(ValueError):
        coords_mid(coords)



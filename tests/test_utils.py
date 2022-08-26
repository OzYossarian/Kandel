import random
import statistics
import pytest
from collections import Counter
from typing import Callable, Iterable, List

from main.utils.types import Coordinates
from main.utils.utils import modulo_duplicates, coords_mid, coords_sum, coords_minus, embed_coords
from tests.utils.coordinates import random_coordss, random_coords
from tests.utils.numbers import default_test_repeats_medium


def test_modulo_duplicates():
    # Explicit tests:
    xs = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5]
    with pytest.raises(ZeroDivisionError):
        assert modulo_duplicates(xs, 0) == []

    assert modulo_duplicates(xs, 1) == []
    assert modulo_duplicates(xs, 2) == [1, 3, 5]
    assert modulo_duplicates(xs, 3) == [1, 2, 2, 4, 5, 5]
    assert modulo_duplicates(xs, 4) == [1, 2, 2, 3, 3, 3, 5]
    assert modulo_duplicates(xs, 5) == [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]

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


def test_coords_mid_fails_given_empty_sequence():
    expected_error = \
        "Can't find the midpoint of an empty sequence of coordinates"
    with pytest.raises(ValueError, match=expected_error):
        coords_mid(*[])


def test_coords_mid_if_all_coords_tuples():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        num_coordss = random.randint(1, 100)
        coordss = random_coordss(num_coordss, dimension=dimension)
        result = coords_mid(*coordss)
        expected = tuple([
            statistics.mean([coords[d] for coords in coordss])
            for d in range(dimension)])
        assert result == expected


def test_coords_mid_if_all_coords_not_tuples():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        num_coordss = random.randint(1, 100)
        coordss = random_coordss(num_coordss, tuple_coords=False)
        result = coords_mid(*coordss)
        expected = statistics.mean(coordss)
        assert result == expected


def test_coords_mid_fails_if_lengths_unequal():
    coords = [0, (1, 1)]
    expected_error = \
        "Can't find the midpoint of coordinates of different lengths"
    with pytest.raises(ValueError, match=expected_error):
        coords_mid(*coords)

    coords = [(0, 0), (1, 1, 1)]
    with pytest.raises(ValueError, match=expected_error):
        coords_mid(*coords)


def test_coords_sum_fails_given_empty_sequence():
    expected_error = \
        "Can't find the sum of an empty sequence of coordinates"
    with pytest.raises(ValueError, match=expected_error):
        coords_sum(*[])


def test_coords_sum_if_all_coords_tuples():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        num_coordss = random.randint(1, 100)
        coordss = random_coordss(num_coordss, dimension=dimension)
        result = coords_sum(*coordss)
        expected = tuple([
            sum([coords[d] for coords in coordss])
            for d in range(dimension)])
        assert result == expected


def test_coords_sum_if_all_coords_not_tuples():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        num_coordss = random.randint(1, 100)
        coordss = random_coordss(num_coordss, tuple_coords=False)
        result = coords_sum(*coordss)
        expected = sum(coordss)
        assert result == expected


def test_coords_sum_fails_if_lengths_unequal():
    expected_error = \
        "Can't sum over coordinates of different lengths"
    coords = [0, (1, 1)]
    with pytest.raises(ValueError, match=expected_error):
        coords_sum(*coords)

    coords = [(0, 0), (1, 1, 1)]
    with pytest.raises(ValueError, match=expected_error):
        coords_sum(*coords)


def _test_coords_minus(
        create_coords: Callable[[int], Coordinates],
        get_expected: Callable[[Coordinates, Coordinates], Coordinates]):
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        xs = create_coords(dimension)
        ys = create_coords(dimension)
        result = coords_minus(xs, ys)
        expected = get_expected(xs, ys)
        assert result == expected


def test_coords_minus_if_all_coords_tuples():
    def create_coordss(dimension: int):
        return random_coords(dimension=dimension)

    def get_expected(xs: Coordinates, ys: Coordinates):
        return tuple(x - y for x, y in zip(xs, ys))

    _test_coords_minus(create_coordss, get_expected)


def test_coords_minus_if_all_coords_not_tuples():
    def create_coordss(dimension: int):
        return random_coords(tuple_coords=False)

    def get_expected(x: Coordinates, y: Coordinates):
        return x - y

    _test_coords_minus(create_coordss, get_expected)


def test_coords_minus_fails_if_lengths_unequal():
    expected_error = \
        "Can't find difference of coordinates of different lengths"
    x, ys = 0, (1, 1)
    with pytest.raises(ValueError, match=expected_error):
        coords_minus(x, ys)

    xs, ys = (0, 0), (1, 1, 1)
    with pytest.raises(ValueError, match=expected_error):
        coords_minus(xs, ys)


def test_embed_coords_fails_if_dimension_too_low():
    coords = (0, 1)
    dimension = 2
    expected_error = "dimension must be greater than that of the coordinates"
    with pytest.raises(ValueError, match=expected_error):
        embed_coords(coords, dimension)


def test_embed_coords_fails_if_offset_dimension_is_wrong():
    coords = (0, 1)
    dimension = 3
    offset = (1, 1)
    expected_error = f"offset does not have dimension {dimension}"
    with pytest.raises(ValueError, match=expected_error):
        embed_coords(coords, dimension, offset=offset)


def test_embed_coords_fails_if_hyperplane_dimension_is_wrong():
    coords = (0, 1)
    dimension = 3
    hyperplane = (1, 1, 1)
    expected_error = "dimensions of coordinates and hyperplane don't match"
    with pytest.raises(ValueError, match=expected_error):
        embed_coords(coords, dimension, hyperplane=hyperplane)


def test_embed_coords_fails_if_exactly_one_of_coords_and_hyperplane_is_tuple():
    coords = 0
    dimension = 2
    hyperplane = (1,)
    expected_error = "types of coordinates and hyperplane don't match"
    with pytest.raises(ValueError, match=expected_error):
        embed_coords(coords, dimension, hyperplane=hyperplane)

    coords = (0,)
    dimension = 2
    hyperplane = 1
    with pytest.raises(ValueError, match=expected_error):
        embed_coords(coords, dimension, hyperplane=hyperplane)


def test_embed_coords_if_coords_is_tuple():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        coords_dim = random.randint(1, 100)
        coords = random_coords(dimension=coords_dim)
        space_dim = random.randint(coords_dim + 1, 2 * (coords_dim + 1))
        offset = random_coords(dimension=space_dim)
        hyperplane = tuple(random.sample(range(space_dim), k=coords_dim))

        result = embed_coords(coords, space_dim, offset, hyperplane)
        expected = list(offset)
        for i in range(coords_dim):
            expected[hyperplane[i]] += coords[i]
        expected = tuple(expected)

        assert result == expected


def test_embed_coords_if_coords_is_not_tuple():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        coords_dim = 1
        coords = random_coords(tuple_coords=False)
        space_dim = random.randint(coords_dim + 1, 2 * (coords_dim + 1))
        offset = random_coords(dimension=space_dim)
        hyperplane = random.randint(0, space_dim-1)

        result = embed_coords(coords, space_dim, offset, hyperplane)
        expected = list(offset)
        expected[hyperplane] += coords
        expected = tuple(expected)

        assert result == expected


def test_embed_coords_if_offset_is_None():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        coords_dim = random.randint(1, 100)
        coords = random_coords(dimension=coords_dim)
        space_dim = random.randint(coords_dim + 1, 2 * (coords_dim + 1))
        offset = None  # `offset` should then default to 0 vector
        hyperplane = tuple(random.sample(range(space_dim), k=coords_dim))

        result = embed_coords(coords, space_dim, offset, hyperplane)
        expected = [0 for _ in range(space_dim)]
        for i in range(coords_dim):
            expected[hyperplane[i]] += coords[i]
        expected = tuple(expected)

        assert result == expected


def test_embed_coords_if_hyperplane_is_None():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        coords_dim = random.randint(1, 100)
        coords = random_coords(dimension=coords_dim)
        space_dim = random.randint(coords_dim + 1, 2 * (coords_dim + 1))
        offset = random_coords(dimension=space_dim)
        hyperplane = None

        result = embed_coords(coords, space_dim, offset, hyperplane)
        expected = list(offset)
        for i in range(coords_dim):
            expected[i] += coords[i]
        expected = tuple(expected)

        assert result == expected

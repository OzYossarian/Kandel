import random

from main.building_blocks.Qubit import Qubit
from tests.utils.coordinates import random_coords
from tests.utils.numbers import default_test_repeats_small


def test_qubit_dimension_when_coords_non_tuple():
    repeats = default_test_repeats_small
    for _ in range(repeats):
        coords = random_coords(tuple_coords=False)
        qubit = Qubit(coords)
        assert qubit.dimension == 1


def test_qubit_dimension_when_coords_tuple():
    repeats = default_test_repeats_small
    for _ in range(repeats):
        dimension = random.randint(1, 100)
        coords = random_coords(dimension=dimension)
        qubit = Qubit(coords)
        assert qubit.dimension == dimension


def test_qubit_repr():
    coords = 0
    qubit = Qubit(coords)
    assert str(qubit) == str({'coords': coords})

    coords = (0, 0)
    qubit = Qubit(coords)
    assert str(qubit) == str({'coords': coords})


import random

from main.building_blocks.Qubit import Qubit
from tests.utils.coordinates import random_non_tuple_coords, random_tuple_coords


def test_qubit_dimension():
    repeats = 10
    for _ in range(repeats):
        coords = random_non_tuple_coords(-100, 100)
        qubit = Qubit(coords)
        assert qubit.dimension == 1

    for _ in range(repeats):
        dimension = random.randint(1, 100)
        coords = random_tuple_coords(dimension, -100, 100)
        qubit = Qubit(coords)
        assert qubit.dimension == dimension


def test_qubit_repr():
    coords = 0
    qubit = Qubit(coords)
    assert str(qubit) == str({'coords': coords})

    coords = (0, 0)
    qubit = Qubit(coords)
    assert str(qubit) == str({'coords': coords})


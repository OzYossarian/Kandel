import random

from main.building_blocks.Qubit import Qubit
from tests.utils.numbers import random_int_or_float, random_tuple_mixed_int_or_float


def test_qubit_dimension():
    repeats = 10
    for _ in range(repeats):
        coords = random_int_or_float(-100, 100)
        qubit = Qubit(coords)
        assert qubit.dimension == 1

    for _ in range(repeats):
        dimension = random.randint(1, 100)
        coords = random_tuple_mixed_int_or_float(dimension, -100, 100)
        qubit = Qubit(coords)
        assert qubit.dimension == dimension


def test_qubit_repr():
    coords = 0
    qubit = Qubit(coords)
    assert str(qubit) == str({'coords': coords})

    coords = (0, 0)
    qubit = Qubit(coords)
    assert str(qubit) == str({'coords': coords})


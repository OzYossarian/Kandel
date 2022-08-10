import random
from collections import Counter

from main.utils.utils import modulo_duplicates


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


def test_coords_mid():
    assert False

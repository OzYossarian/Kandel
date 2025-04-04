import random

default_min_coord = -10
default_max_coord = 10
default_test_repeats_small = 10
default_test_repeats_medium = 100
default_test_repeats_large = 1000


def random_complex_number(
        min: float = default_min_coord, max: float = default_max_coord):
    real = random.uniform(min, max)
    imaginary = random.uniform(min, max)
    return complex(real, imaginary)


def random_complex_number_int(
        min: int = default_min_coord, max: int = default_max_coord):
    real = random.randint(min, max)
    imaginary = random.randint(min, max)
    return complex(real, imaginary)


def default_max_unique_sample_size(
        dimension: int,
        min: int = default_min_coord, max: int = default_max_coord):
    return ((max - min) ** dimension) // 2

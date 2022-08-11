import random


def random_complex_number(min: float = -10, max: float = 10):
    real = random.uniform(min, max)
    imaginary = random.uniform(min, max)
    return complex(real, imaginary)


def random_complex_number_int(min: int, max: int):
    real = random.randint(min, max)
    imaginary = random.randint(min, max)
    return complex(real, imaginary)

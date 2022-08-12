import random


def random_tuple_mixed_int_or_float(size: int, min: int, max: int):
    return tuple(random_int_or_float(min, max) for _ in range(size))


def random_int_or_float(min: int, max: int):
    number_type = random.randint(0, 1)
    if number_type == 0:
        # Return int
        return random.randint(min, max)
    else:
        # Return float
        return random.uniform(min, max)


def random_complex(min: float, max: float):
    real = random.uniform(min, max)
    imaginary = random.uniform(min, max)
    return complex(real, imaginary)


def random_int_or_float_or_complex(min: int, max: int):
    # For complex numbers, the (min, max) bound applies to each of the real
    # and imaginary components individually.
    number_type = random.randint(0, 2)
    if number_type < 2:
        return random_int_or_float(min, max)
    else:
        return random_complex(min, max)
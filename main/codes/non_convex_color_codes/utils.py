# Child of Hexagonal code
import itertools as it
from typing import Tuple


def generate_triangular_lattice(t, center: Tuple[int], orientation_flipped: bool = False) -> set:
    """
    """
    coordinates = set()

    if orientation_flipped:
        max_val = -3*t - 1
        sum_val = -3*t
        uncorrected_center = (-t, -t, -t)
        step = -1

    else:
        max_val = 3*t + 1
        sum_val = 3*t
        uncorrected_center = (t, t, t)
        step = 1

    coordinate_shift = tuple(
        [center[i] - uncorrected_center[i] for i in range(3)])
    for combo in it.combinations_with_replacement(range(0, max_val, step), 3):
        if sum(combo) == sum_val:
            for perm in it.permutations(combo):
                coordinates.add((perm[0] + coordinate_shift[0],
                                perm[1] + coordinate_shift[1], perm[2] + coordinate_shift[2]))
    return (coordinates)

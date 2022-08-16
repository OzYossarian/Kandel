from main.building_blocks.Qubit import Qubit
from tests.utils.coordinates import random_tuple_coords, random_non_tuple_coords, unique_random_tuple_coords, \
    unique_random_tuple_coords_int, random_tuple_coords_int
from tests.utils.numbers import default_min_coord, default_max_coord


def random_qubit_tuple_coords(
        dimension: int,
        min: float = default_min_coord, max: float = default_max_coord):
    coords = random_tuple_coords(dimension, min, max)
    return Qubit(coords)


def random_qubit_tuple_coords_int(
        dimension: int,
        min: int = default_min_coord, max: int = default_max_coord):
    coords = random_tuple_coords_int(dimension, min, max)
    return Qubit(coords)


def random_qubit_non_tuple_coords(
        min: float = default_min_coord, max: float = default_max_coord):
    coords = random_non_tuple_coords(min, max)
    return Qubit(coords)


def unique_random_qubits_tuple_coords(
        num: int, dimension: int,
        min: float = default_min_coord, max: float = default_max_coord):
    coordss = unique_random_tuple_coords(num, dimension, min, max)
    qubits = [Qubit(coords) for coords in coordss]
    return qubits


def unique_random_qubits_tuple_coords_int(
        num: int, dimension: int,
        min: int = default_min_coord, max: int = default_max_coord):
    coordss = unique_random_tuple_coords_int(num, dimension, min, max)
    qubits = [Qubit(coords) for coords in coordss]
    return qubits
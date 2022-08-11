from main.building_blocks.Qubit import Qubit
from tests.utils.coordinates import random_tuple_coords, random_non_tuple_coords, unique_random_tuple_coords, \
    unique_random_tuple_coords_int, random_tuple_coords_int


def random_qubit_tuple_coords(dimension: int, min: float = -10, max: float = 10):
    coords = random_tuple_coords(dimension, min, max)
    return Qubit(coords)


def random_qubit_tuple_coords_int(dimension: int, min: int = -10, max: int = 10):
    coords = random_tuple_coords_int(dimension, min, max)
    return Qubit(coords)


def random_qubit_non_tuple_coords(min: float = -10, max: float = 10):
    coords = random_non_tuple_coords(min, max)
    return Qubit(coords)


def unique_random_qubits_tuple_coords(
        num: int, dimension: int, min: float = -10, max: float = 10):
    coordss = unique_random_tuple_coords(num, dimension, min, max)
    qubits = [Qubit(coords) for coords in coordss]
    return qubits


def unique_random_qubits_tuple_coords_int(
        num: int, dimension: int, min: int = -10, max: int = 10):
    coordss = unique_random_tuple_coords_int(num, dimension, min, max)
    qubits = [Qubit(coords) for coords in coordss]
    return qubits
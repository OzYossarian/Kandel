from main.building_blocks.Qubit import Qubit
from tests.utils.utils_coordinates import random_coordss
from tests.utils.utils_numbers import default_min_coord, default_max_coord


def random_qubit(
        int_coords: bool = False,
        tuple_coords: bool = True,
        dimension: int = None,
        min_coord: int | float = default_min_coord,
        max_coord: int | float = default_max_coord):
    qubits = random_qubits(
        num=1,
        int_coords=int_coords,
        tuple_coords=tuple_coords,
        dimension=dimension,
        min_coord=min_coord,
        max_coord=max_coord)
    return qubits[0]


def random_qubits(
        num: int,
        unique: bool = False,
        int_coords: bool = False,
        tuple_coords: bool = True,
        dimension: int = None,
        max_dimension: int = None,
        min_coord: int | float = default_min_coord,
        max_coord: int | float = default_max_coord
):
    coordss = random_coordss(
        num,
        unique,
        int_coords,
        tuple_coords,
        dimension,
        max_dimension,
        min_coord,
        max_coord)
    qubits = [Qubit(coords) for coords in coordss]
    return qubits

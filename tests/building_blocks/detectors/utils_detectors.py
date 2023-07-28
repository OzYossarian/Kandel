import random
from typing import List, Union

from main.building_blocks.detectors.Detector import Detector
from main.utils.utils import xor
from tests.building_blocks.utils_checks import hermitian_signs, random_checks
from tests.utils.utils_coordinates import random_coords
from tests.utils.utils_numbers import default_min_coord, default_max_coord


def random_detectors(
        num: int,
        int_coords: bool = False,
        tuple_coords: bool = True,
        checks_per_detector: int = None,
        max_checks_per_detector: int = None,
        checks_weight: int = None,
        max_checks_weight: int = None,
        dimension: int = None,
        max_dimension: int = None,
        zero_anchors: bool = False,
        random_anchors: bool = False,
        from_letters: List[str] = None,
        from_signs: List[str] = None,
        min_coord: Union[float,int] = default_min_coord,
        max_coord: Union[float, int] = default_max_coord
):
    validate_random_detectors_arguments(
        checks_per_detector,
        max_checks_per_detector,
        dimension,
        max_dimension,
        tuple_coords,
        checks_weight,
        max_checks_weight)

    if not tuple_coords:
        dimension = 1

    nums_checks = [checks_per_detector for _ in range(num)] \
        if checks_per_detector is not None \
        else random.choices(range(1, max_checks_per_detector + 1), k=num)

    dimensions = [dimension for _ in range(num)] \
        if dimension is not None else \
        random.choices(range(1, max_dimension + 1), k=num)

    detectors = [
        random_detector(
            nums_checks[i],
            dimensions[i],
            int_coords,
            tuple_coords,
            checks_weight,
            max_checks_weight,
            zero_anchors,
            random_anchors,
            from_letters,
            from_signs,
            min_coord,
            max_coord)
        for i in range(num)]
    return detectors


def random_detector(
        num_checks: int,
        dimension: int,
        int_coords: bool = False,
        tuple_coords: bool = True,
        checks_weight: int = None,
        max_checks_weight: int = None,
        zero_anchors: bool = False,
        random_anchors: bool = False,
        from_letters: List[str] = None,
        from_signs: List[str] = None,
        min_coord: Union[float, int] = default_min_coord,
        max_coord: Union[float, int] = default_max_coord
):
    validate_random_detector_arguments(
        num_checks,
        dimension,
        tuple_coords,
        zero_anchors,
        random_anchors)

    if not tuple_coords:
        dimension = 1

    checks = random_checks(
        num=num_checks,
        int_coords=int_coords,
        tuple_coords=tuple_coords,
        weight=checks_weight,
        max_weight=max_checks_weight,
        dimension=dimension,
        zero_anchors=zero_anchors,
        random_anchors=random_anchors,
        from_letters=from_letters,
        from_signs=from_signs,
        min_coord=min_coord,
        max_coord=max_coord,)

    times = random.choices(range(-10, 1), k=num_checks-1)
    # At least one check must occur at the `end` round
    times.append(0)
    timed_checks = [(time, check) for time, check in zip(times, checks)]

    end = random.randint(0, 100)

    if zero_anchors:
        anchor = 0 \
            if not tuple_coords \
            else tuple(0 for _ in range(dimension))
    elif random_anchors:
        anchor = random_coords(
            int_coords, tuple_coords, dimension, min_coord, max_coord)
    else:
        # Let constructor decide
        anchor = None

    return Detector(timed_checks, end, anchor)


def validate_random_detectors_arguments(
        checks_per_detector: int,
        max_checks_per_detector: int,
        dimension: int,
        max_dimension: int,
        tuple_coords: bool,
        checks_weight: int,
        max_checks_weight: int,
):
    assert checks_per_detector is None or max_checks_per_detector is None
    num_checks_arg = checks_per_detector \
        if checks_per_detector is not None \
        else max_checks_per_detector
    assert num_checks_arg > 0

    if tuple_coords:
        assert xor(dimension is None, max_dimension is None)

    assert xor(checks_weight is None, max_checks_weight is None)
    checks_weight_arg = checks_weight \
        if checks_weight is not None \
        else max_checks_weight
    assert checks_weight_arg > 0


def validate_random_detector_arguments(
        num_checks: int,
        dimension: int,
        tuple_coords: bool,
        zero_anchors: bool,
        random_anchors: bool,
):
    assert num_checks > 0
    if tuple_coords:
        assert dimension > 0
    else:
        assert dimension in [None, 1]

    assert zero_anchors is False or random_anchors is False
    # Here we allow both to be False - this just means anchors will be set
    # to the default in the Detector constructor. Currently this default is
    # the mean of all Checks' anchors.

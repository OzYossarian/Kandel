import random
from typing import List

from main.Colour import Colour
from main.building_blocks.Check import Check
from main.utils.types import Coordinates
from main.utils.utils import xor
from tests.utils.colours import random_colour
from tests.utils.coordinates import random_coords
from tests.utils.numbers import default_max_unique_sample_size, default_min_coord, default_max_coord
from tests.utils.paulis import random_paulis


# If all signs of all Paulis in a Check are 1 or -1, we're guaranteed that the
# product is Hermitian.
hermitian_signs = [1, -1]


def random_checks(
        num: int,
        int_coords: bool = False,
        tuple_coords: bool = True,
        weight: int = None,
        max_weight: int = None,
        dimension: int = None,
        max_dimension: int = None,
        zero_anchors: bool = False,
        random_anchors: bool = False,
        random_colours: bool = False,
        from_colours: List[Colour] = None,
        from_letters: List[str] = None,
        from_signs: List[str] = None,
        min_coord: float | int = default_min_coord,
        max_coord: float | int = default_max_coord
):
    """
    A method to generate `num` Check objects, with various settings.

    Args:
        num:
            how many checks to generate.
        int_coords:
            whether the coordinates should be strictly integers
        tuple_coords:
            whether the coordinates should be tuples
        weight:
            the weight of all the checks, if all the same. Leave as None if
            weights are allowed to vary
        max_weight:
            the max weight of all the checks, if weight can vary. Leave as
            None if weights are all the same
        dimension:
            the dimension of all the checks, if all the same. Leave as None if
            dimensions are allowed to vary, or if non-tuple coordinates are
            requested (since then dimension must be 1).
        max_dimension:
            the max dimension of all the checks, if dimension can vary. Leave
            as None if dimensions are fixed, or if non-tuple coordinates are
            requested (since then dimension must be 1).
        zero_anchors:
            if True, all checks' anchors are set to the zero vector in the
            appropriate dimension (or just 0, if non-tuple coords used).
            Defaults to False.
        random_anchors:
            if True, all checks' anchors are set to a random vector in the
            appropriate dimension (or just a random number, if non-tuple
            coords used). Defaults to False.
        random_colours:
            if True, checks are assigned randomly chosen colours from
            `from_colours`. If `from_colours` is not None, `random_colours`
            will automatically be set to True.
        from_colours:
            colours to choose randomly from for each check. If None, and
            `random_colours` is True, this defaults to all possible colours.
            If instead `from_colours` is False, this remains None, and no
            colours are assigned to checks.
        from_letters:
            letters to choose from when creating the Paulis that will be used
            in the checks. Defaults to ['I', 'X', 'Y', 'Z'].
        from_signs:
            signs to choose from when creating the Paulis that will be used
            in the checks. Defaults to [1, -1] to ensure the Check is
            Hermitian.
        min_coord:
            minimum value to be used in any coordinate component. Defaults to
            `default_min_coord`, which is -10 at time of writing.
        max_coord:
            maximum value to be used in any coordinate component. Defaults to
            `default_max_coord`, which is 10 at time of writing.

    Returns:
        a list of `num` randomly generated checks.

    """
    validate_arguments(
        tuple_coords,
        weight,
        max_weight,
        dimension,
        max_dimension,
        zero_anchors,
        random_anchors,
        from_colours)
    # Because of the uniqueness constraint on the qubits in a single check,
    # we can't just get all the Paulis at once and then chunk them up into
    # checks. We could get round this by getting a set of Paulis on unique
    # qubits all at once, and then chunk these up. But then this isn't as
    # general as it needs to be - it's perfectly reasonable for two different
    # checks to contain the same qubit.

    if not tuple_coords:
        dimension = 1

    checks = []
    for _ in range(num):
        # Get dimension for this check
        check_dimension = dimension \
            if dimension is not None \
            else random.randint(1, max_dimension)
        # Then get weight
        if weight is not None:
            check_weight = weight
        else:
            max_check_weight = default_max_unique_sample_size(
                check_dimension, min_coord, max_coord)
            max_check_weight = min(max_weight, max_check_weight)
            check_weight = random.randint(1, max_check_weight)

        # Get anchor for this check
        if zero_anchors:
            anchor = 0 \
                if not tuple_coords \
                else tuple(0 for _ in range(check_dimension))
        elif random_anchors:
            anchor = random_coords(
                int_coords, tuple_coords, dimension, min_coord, max_coord)
        else:
            # Let Check constructor decide
            anchor = None

        # Then get colour
        if from_colours is not None:
            colour = random.choice(from_colours)
        elif random_colours:
            colour = random_colour()
        else:
            # No colour
            colour = None

        check = random_check(
            int_coords,
            tuple_coords,
            check_weight,
            check_dimension,
            from_letters,
            from_signs,
            anchor,
            colour,
            min_coord,
            max_coord)
        checks.append(check)

    return checks


def random_check(
        int_coords: bool = False,
        tuple_coords: bool = True,
        weight: int = None,
        dimension: int = None,
        from_letters: List[str] = None,
        from_signs: List[str] = None,
        anchor: Coordinates = None,
        colour: Colour = None,
        min_coord: float | int = default_min_coord,
        max_coord: float | int = default_max_coord
):
    if from_signs is None:
        from_signs = hermitian_signs

    # All qubits within a check must be unique
    unique_qubits = True
    # All dimensions within a check must be the same
    max_dimension = None

    paulis = random_paulis(
        weight,
        unique_qubits,
        int_coords,
        tuple_coords,
        dimension,
        max_dimension,
        from_letters,
        from_signs,
        min_coord,
        max_coord)

    check = Check(paulis, anchor, colour)
    return check


def validate_arguments(
        tuple_coords: bool,
        weight: int,
        max_weight: int,
        dimension: int,
        max_dimension: int,
        zero_anchors: bool,
        random_anchors: bool,
        from_colours: List[Colour]
):
    assert xor(weight is None, max_weight is None)
    weight_arg = weight if weight is not None else max_weight
    assert weight_arg > 0

    if tuple_coords:
        assert xor(dimension is None, max_dimension is None)
        dim_arg = dimension if dimension is not None else max_dimension
        assert dim_arg > 0
    else:
        assert dimension in [None, 1]
        assert max_dimension in [None, 1]

    assert zero_anchors is False or random_anchors is False
    # Here we allow both to be False - this just means anchors will be set
    # to the default in the Check constructor. Currently this default is the
    # mean of all qubits' coordinates.

    if from_colours is not None:
        assert from_colours != []




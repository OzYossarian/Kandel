import random
from typing import List

from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.utils.utils import xor
from tests.utils.utils_numbers import default_max_unique_sample_size, default_min_coord, default_max_coord
from tests.building_blocks.pauli.utils_paulis import random_paulis


# If all signs of all Paulis in a LogicalOperator are 1 or -1, we're
# guaranteed that the product is Hermitian.
hermitian_signs = [1, -1]


def random_logical_operators(
        num: int,
        int_coords: bool = False,
        tuple_coords: bool = True,
        weight: int = None,
        max_weight: int = None,
        dimension: int = None,
        max_dimension: int = None,
        from_letters: List[str] = None,
        from_signs: List[str] = None,
        min_coord: float | int = default_min_coord,
        max_coord: float | int = default_max_coord
):
    """
    A method to generate `num` LogicalOperator objects, with various settings.

    Args:
        num:
            how many operators to generate.
        int_coords:
            whether the coordinates should be strictly integers
        tuple_coords:
            whether the coordinates should be tuples
        weight:
            the weight of all the operators, if all the same. Leave as None if
            weights are allowed to vary
        max_weight:
            the max weight of all the operators, if weight can vary. Leave as
            None if weights are all the same
        dimension:
            the dimension of all the operators, if all the same. Leave as None if
            dimensions are allowed to vary, or if non-tuple coordinates are
            requested (since then dimension must be 1).
        max_dimension:
            the max dimension of all the operators, if dimension can vary. Leave
            as None if dimensions are fixed, or if non-tuple coordinates are
            requested (since then dimension must be 1).
        from_letters:
            letters to choose from when creating the Paulis that will be used
            in the operators. Defaults to ['I', 'X', 'Y', 'Z'].
        from_signs:
            signs to choose from when creating the Paulis that will be used
            in the operators. Defaults to [1, -1] to ensure the operator is
            Hermitian.
        min_coord:
            minimum value to be used in any coordinate component. Defaults to
            `default_min_coord`, which is -10 at time of writing.
        max_coord:
            maximum value to be used in any coordinate component. Defaults to
            `default_max_coord`, which is 10 at time of writing.

    Returns:
        a list of `num` randomly generated operators.

    """
    validate_random_logical_operators_arguments(
        tuple_coords,
        weight,
        max_weight,
        dimension,
        max_dimension)
    # Because of the uniqueness constraint on the qubits in a single operator,
    # we can't just get all the Paulis at once and then chunk them up into
    # operators. We could get round this by getting a set of Paulis on unique
    # qubits all at once, and then chunk these up. But then this isn't as
    # general as it needs to be - it's perfectly reasonable for two different
    # operators to contain the same qubit.

    if not tuple_coords:
        dimension = 1

    operators = []
    for _ in range(num):
        # Get dimension for this operator
        operator_dimension = dimension \
            if dimension is not None \
            else random.randint(1, max_dimension)
        # Then get weight
        if weight is not None:
            operator_weight = weight
        else:
            max_operator_weight = default_max_unique_sample_size(
                operator_dimension, min_coord, max_coord)
            max_operator_weight = min(max_weight, max_operator_weight)
            operator_weight = random.randint(1, max_operator_weight)

        operator = random_logical_operator(
            operator_weight,
            operator_dimension,
            int_coords,
            tuple_coords,
            from_letters,
            from_signs,
            min_coord,
            max_coord)
        operators.append(operator)

    return operators


def random_logical_operator(
        weight: int,
        dimension: int = None,
        int_coords: bool = False,
        tuple_coords: bool = True,
        from_letters: List[str] = None,
        from_signs: List[str] = None,
        min_coord: float | int = default_min_coord,
        max_coord: float | int = default_max_coord
):
    validate_random_logical_operator_arguments(
        weight, dimension, tuple_coords)

    if tuple_coords is None:
        dimension = 1
    if from_signs is None:
        from_signs = hermitian_signs

    # All qubits within an operator must be unique
    unique_qubits = True
    # All dimensions within an operator must be the same
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

    operator = LogicalOperator(paulis)
    return operator


def validate_random_logical_operators_arguments(
        tuple_coords: bool,
        weight: int,
        max_weight: int,
        dimension: int,
        max_dimension: int,
):
    assert xor(weight is None, max_weight is None)
    if tuple_coords:
        assert xor(dimension is None, max_dimension is None)


def validate_random_logical_operator_arguments(
        weight: int,
        dimension: int,
        tuple_coords: bool,
):
    assert weight > 0
    if tuple_coords:
        assert dimension > 0
    else:
        assert dimension in [None, 1]

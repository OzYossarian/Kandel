import random

import pytest

from main.building_blocks.Qubit import Qubit
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from tests.building_blocks.logical.utils_logical_operators import random_logical_operator
from tests.utils.utils_numbers import default_test_repeats_medium, default_max_unique_sample_size


def test_logical_qubit_fails_if_all_operators_None():
    expected_error = \
        "At least one operator on a logical qubit must be non-None"
    with pytest.raises(ValueError, match=expected_error):
        LogicalQubit()


def test_logical_qubit_fails_if_dimensions_unequal():
    expected_error = \
        "All operators within a logical qubit must have the same dimensions"
    # Explicit test:
    x = LogicalOperator([Pauli(Qubit((0, 0, 0)), PauliLetter('X'))])
    z = LogicalOperator([Pauli(Qubit((0, 0)), PauliLetter('Z'))])
    with pytest.raises(ValueError, match=expected_error):
        LogicalQubit(x=x, z=z)

    # Random tests:
    for _ in range(default_test_repeats_medium):
        # Either pick 2 or 3 operators to be non-None
        num_non_none_ops = random.randint(2, 3)
        # Pick distinct dimensions for each operator
        dimensions = random.sample(range(1, 10), k=num_non_none_ops)
        # Pick a random weight for each operator
        weights = random.choices(range(1, 20), k=num_non_none_ops)

        # Create randomly generated operators.
        operators = []
        for i in range(num_non_none_ops):
            dimension = dimensions[i]
            weight = min(weights[i], default_max_unique_sample_size(dimension))
            operators.append(random_logical_operator(
                int_coords=True,
                weight=weight,
                dimension=dimension))

        # Randomly pick which ones are X, Y and Z operators.
        xyz = [None, None, None]
        operator_indexes = [0, 1, 2] \
            if num_non_none_ops == 3 \
            else random.sample(range(2), k=2)
        for i in range(num_non_none_ops):
            xyz[operator_indexes[i]] = operators[i]

        # Assert that this raises an error
        with pytest.raises(ValueError, match=expected_error):
            LogicalQubit(xyz[0], xyz[1], xyz[2])


def test_logical_qubit_fails_if_coords_types_unequal():
    expected_error = \
        "Either all operators within a logical qubit should have tuple " \
        "coordinates, or none of them should"
    # Explicit test:
    x = LogicalOperator([Pauli(Qubit((0,)), PauliLetter('X'))])
    z = LogicalOperator([Pauli(Qubit(0), PauliLetter('Z'))])
    with pytest.raises(ValueError, match=expected_error):
        LogicalQubit(x=x, z=z)

    # Random tests:
    for _ in range(default_test_repeats_medium):
        # Either pick 2 or 3 operators to be non-None
        num_tuple_operators = random.randint(1, 2)
        num_non_tuple_operators = random.randint(1, 3-num_tuple_operators)

        operators = []
        # Create randomly generated tuple operators.
        for i in range(num_tuple_operators):
            max_weight = random.randint(1, 20)
            weight = min(max_weight, default_max_unique_sample_size(1))
            operators.append(random_logical_operator(
                int_coords=True,
                weight=weight,
                dimension=1))
        # Create randomly generated non-tuple operators.
        for i in range(num_non_tuple_operators):
            max_weight = random.randint(1, 20)
            weight = min(max_weight, default_max_unique_sample_size(1))
            operators.append(random_logical_operator(
                int_coords=True,
                weight=weight,
                tuple_coords=False))

        # Randomly pick which ones are X, Y and Z operators.
        num_non_none_operators = num_tuple_operators + num_non_tuple_operators
        xyz = [None, None, None]
        operator_indexes = [0, 1, 2] \
            if num_non_none_operators == 3 \
            else random.sample(range(2), k=2)
        for i in range(num_non_none_operators):
            xyz[operator_indexes[i]] = operators[i]

        # Assert that this raises an error
        with pytest.raises(ValueError, match=expected_error):
            LogicalQubit(xyz[0], xyz[1], xyz[2])


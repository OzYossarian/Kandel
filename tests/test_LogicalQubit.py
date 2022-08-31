import random

import pytest

from main.building_blocks.Qubit import Qubit
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter


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


def test_logical_qubit_fails_if_coords_types_unequal():
    expected_error = \
        "Either all operators within a logical qubit should have tuple " \
        "coordinates, or none of them should"
    # Explicit test:
    x = LogicalOperator([Pauli(Qubit((0,)), PauliLetter('X'))])
    z = LogicalOperator([Pauli(Qubit(0), PauliLetter('Z'))])
    with pytest.raises(ValueError, match=expected_error):
        LogicalQubit(x=x, z=z)


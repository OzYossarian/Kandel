import random

import pytest

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.syndrome_extraction.controlled_gate_orderers.RotatedSurfaceCodeOrderer import \
    RotatedSurfaceCodeOrderer
from tests.building_blocks.utils_checks import random_check
from tests.utils.utils_coordinates import random_coords
from tests.utils.utils_numbers import default_test_repeats_medium, default_max_unique_sample_size


def test_rotated_surface_code_orderer_fails_on_unexpected_weight():
    orderer = RotatedSurfaceCodeOrderer()
    expected_error = "Check has unexpected weight"

    # Explicit test:
    paulis = [
        Pauli(Qubit(0), PauliLetter('X')),
        Pauli(Qubit(1), PauliLetter('X')),
        Pauli(Qubit(2), PauliLetter('X'))]
    check = Check(paulis)
    with pytest.raises(ValueError, match=expected_error):
        orderer.order(check)

    # Random tests:
    for _ in range(default_test_repeats_medium):
        dimension = random.randint(1, 10)
        max_weight = min(20, default_max_unique_sample_size(dimension))
        wrong_weights = [
            i for i in range(1, max_weight + 1)
            if i not in [2, 4]]
        weight = random.choice(wrong_weights)
        check = random_check(
            int_coords=True,
            weight=weight,
            dimension=dimension)
        with pytest.raises(ValueError, match=expected_error):
            orderer.order(check)


def test_rotated_surface_code_orderer_fails_on_unexpected_word():
    orderer = RotatedSurfaceCodeOrderer()
    expected_error = "Check has unexpected word"

    # Explicit test:
    paulis = [
        # These three are right...
        Pauli(Qubit((2, 1)), PauliLetter('X')),
        Pauli(Qubit((1, 2)), PauliLetter('X')),
        Pauli(Qubit((0, 1)), PauliLetter('X')),
        # ... but this one's wrong
        Pauli(Qubit((1, 0)), PauliLetter('Z'))]
    check = Check(paulis)
    with pytest.raises(ValueError, match=expected_error):
        orderer.order(check)


def test_rotated_surface_code_orderer_fails_on_unexpected_pauli():
    orderer = RotatedSurfaceCodeOrderer()
    expected_error = "Check contains an unexpected Pauli"

    # Explicit test:
    paulis = [
        # These three are right...
        Pauli(Qubit((2, 1)), PauliLetter('X')),
        Pauli(Qubit((1, 2)), PauliLetter('X')),
        Pauli(Qubit((0, 1)), PauliLetter('X')),
        # But this one's got the wrong coordinates...
        Pauli(Qubit((2, 0)), PauliLetter('X'))]
    check = Check(paulis)
    with pytest.raises(ValueError, match=expected_error):
        orderer.order(check)


def test_rotated_surface_code_orderer_on_XXXX_check():
    orderer = RotatedSurfaceCodeOrderer()

    anchor = random_coords(int_coords=True, dimension=2)
    offsets = [(1, 0), (0, -1), (0, 1), (-1, 0)]
    paulis = [
        Pauli(Qubit(
            (anchor[0] + offset[0], anchor[1] + offset[1])),
            PauliLetter('X'))
        for offset in offsets]
    check = Check(paulis, anchor)
    assert orderer.order(check) == paulis


def test_rotated_surface_code_orderer_on_ZZZZ_check():
    orderer = RotatedSurfaceCodeOrderer()

    anchor = random_coords(int_coords=True, dimension=2)
    offsets = [(1, 0), (0, 1), (0, -1), (-1, 0)]
    paulis = [
        Pauli(Qubit(
            (anchor[0] + offset[0], anchor[1] + offset[1])),
            PauliLetter('Z'))
        for offset in offsets]
    check = Check(paulis, anchor)
    assert orderer.order(check) == paulis


def test_rotated_surface_code_orderer_on_bottom_left_ZZ_check():
    orderer = RotatedSurfaceCodeOrderer()

    anchor = random_coords(int_coords=True, dimension=2)
    offsets = [(1, 0), (0, 1)]
    paulis = [
        Pauli(Qubit(
            (anchor[0] + offset[0], anchor[1] + offset[1])),
            PauliLetter('Z'))
        for offset in offsets]
    check = Check(paulis, anchor)
    assert orderer.order(check) == [paulis[0], paulis[1], None, None]


def test_rotated_surface_code_orderer_on_top_right_ZZ_check():
    orderer = RotatedSurfaceCodeOrderer()

    anchor = random_coords(int_coords=True, dimension=2)
    offsets = [(0, -1), (-1, 0)]
    paulis = [
        Pauli(Qubit(
            (anchor[0] + offset[0], anchor[1] + offset[1])),
            PauliLetter('Z'))
        for offset in offsets]
    check = Check(paulis, anchor)
    assert orderer.order(check) == [None, None, paulis[0], paulis[1]]


def test_rotated_surface_code_orderer_on_bottom_right_XX_check():
    orderer = RotatedSurfaceCodeOrderer()

    anchor = random_coords(int_coords=True, dimension=2)
    offsets = [(0, 1), (-1, 0)]
    paulis = [
        Pauli(Qubit(
            (anchor[0] + offset[0], anchor[1] + offset[1])),
            PauliLetter('X'))
        for offset in offsets]
    check = Check(paulis, anchor)
    assert orderer.order(check) == [None, None, paulis[0], paulis[1]]


def test_rotated_surface_code_orderer_on_top_left_XX_check():
    orderer = RotatedSurfaceCodeOrderer()

    anchor = random_coords(int_coords=True, dimension=2)
    offsets = [(1, 0), (0, -1)]
    paulis = [
        Pauli(Qubit(
            (anchor[0] + offset[0], anchor[1] + offset[1])),
            PauliLetter('X'))
        for offset in offsets]
    check = Check(paulis, anchor)
    assert orderer.order(check) == [paulis[0], paulis[1], None, None]


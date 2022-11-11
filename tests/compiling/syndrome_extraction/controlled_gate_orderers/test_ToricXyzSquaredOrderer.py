import random
import pytest

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.syndrome_extraction.controlled_gate_orderers.ToricXyzSquaredOrderer import ToricXyzSquaredOrderer
from tests.building_blocks.utils_checks import random_check
from tests.utils.utils_coordinates import random_coords
from tests.utils.utils_numbers import default_test_repeats_medium, default_max_unique_sample_size


def test_toric_xyz_sqaured_orderer_fails_on_unexpected_weight():
    orderer = ToricXyzSquaredOrderer()
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
            if i not in [2, 6]]
        weight = random.choice(wrong_weights)
        check = random_check(
            int_coords=True,
            weight=weight,
            dimension=dimension)
        with pytest.raises(ValueError, match=expected_error):
            orderer.order(check)


def test_rotated_surface_code_orderer_fails_on_unexpected_pauli():
    orderer = ToricXyzSquaredOrderer()
    expected_error = "Check contains an unexpected Pauli"

    # Explicit tests:
    paulis = [
        # These five are right...
        Pauli(Qubit((4, 0)), PauliLetter('X')),
        Pauli(Qubit((2, 2)), PauliLetter('Y')),
        Pauli(Qubit((-2, 2)), PauliLetter('Z')),
        Pauli(Qubit((-4, 0)), PauliLetter('X')),
        Pauli(Qubit((-2, -2)), PauliLetter('Y')),
        # But this one's got the wrong coordinates
        Pauli(Qubit((2, -3)), PauliLetter('Z'))]
    check = Check(paulis)
    with pytest.raises(ValueError, match=expected_error):
        orderer.order(check)

    paulis = [
        # Now these five are right...
        Pauli(Qubit((4, 0)), PauliLetter('X')),
        Pauli(Qubit((2, 2)), PauliLetter('Y')),
        Pauli(Qubit((-2, 2)), PauliLetter('Z')),
        Pauli(Qubit((-4, 0)), PauliLetter('X')),
        Pauli(Qubit((-2, -2)), PauliLetter('Y')),
        # ... but this one's got the wrong letter
        Pauli(Qubit((2, -2)), PauliLetter('X'))]
    check = Check(paulis)
    with pytest.raises(ValueError, match=expected_error):
        orderer.order(check)


def test_rotated_surface_code_orderer_on_XYZXYZ_check():
    orderer = ToricXyzSquaredOrderer()

    anchor = random_coords(int_coords=True, dimension=2)
    offsets = [
        (2, -2),
        (4, 0),
        (-2, -2),
        (2, 2),
        (-4, 0),
        (-2, 2)]
    paulis = [
        Pauli(Qubit(
            (anchor[0] + offset[0], anchor[1] + offset[1])),
            PauliLetter(letter))
        for offset, letter in zip(offsets, 'ZXYYXZ')]
    check = Check(paulis, anchor)
    expected = paulis
    assert orderer.order(check) == expected


def test_rotated_surface_code_orderer_on_XX_check():
    orderer = ToricXyzSquaredOrderer()

    anchor = random_coords(int_coords=True, dimension=2)
    offsets = [(2, 0), (-2, 0)]
    paulis = [
        Pauli(Qubit(
            (anchor[0] + offset[0], anchor[1] + offset[1])),
            PauliLetter('X'))
        for offset in offsets]
    check = Check(paulis, anchor)
    expected = [None, paulis[0], None, None, paulis[1], None]
    assert orderer.order(check) == expected
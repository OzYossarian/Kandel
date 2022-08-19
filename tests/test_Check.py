import random
from statistics import mean

import pytest

from main.building_blocks.Check import Check
from tests.utils.colours import random_colour
from tests.utils.coordinates import random_tuple_coords_int, unique_random_tuple_coords_int, \
    unique_random_tuple_coords_int_varying_dims, coords_length, unique_random_non_tuple_coords_int, \
    random_non_tuple_coords_int
from tests.utils.numbers import default_max_unique_sample_size, default_test_repeats_medium, default_test_repeats_small
from tests.utils.paulis import random_grouped_xyz_sign_1_paulis_tuple_coords_int, random_paulis_tuple_coords_int, \
    unique_random_sign_1_paulis_tuple_coords_int, \
    unique_random_xyz_paulis_tuple_coords_int, unique_random_xyz_sign_1_paulis_tuple_coords_int, \
    unique_random_xyz_sign_1_paulis_tuple_coords_int_varying_dims, unique_random_xyz_sign_1_paulis_non_tuple_coords_int


def test_check_fails_if_no_paulis_given():
    with pytest.raises(ValueError):
        _ = Check([])
    with pytest.raises(ValueError):
        _ = Check({})


def test_check_fails_if_qubit_used_more_than_once():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        # Use 1 as min because the test is about whether a qubit is used more
        # than once. Doesn't need to cover the case where there's no qubits.
        max_qubits = random.randint(1, 100)
        num_qubits = min(max_qubits, default_max_unique_sample_size(dimension))
        # Guarantee that we choose more letters than qubits.
        num_letters = random.randint(max_qubits + 1, 3 * max_qubits)

        grouped_paulis = random_grouped_xyz_sign_1_paulis_tuple_coords_int(
            num_qubits, num_letters, dimension)
        paulis = [
            pauli
            for _, paulis in grouped_paulis.items()
            for pauli in paulis]

        with pytest.raises(ValueError):
            _ = Check(paulis)


def test_check_fails_if_not_all_paulis_have_sign_1():
    # TODO - allow -1 signs too in future.
    invalid_signs = [1j, -1, -1j]
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randrange(1, 10)
        max_paulis = random.randrange(1, 100)
        num_paulis = min(
            max_paulis, default_max_unique_sample_size(dimension))
        paulis = unique_random_xyz_paulis_tuple_coords_int(num_paulis, dimension)

        # Pick at least one Pauli to put an invalid sign on.
        num_invalid_signs = random.randint(1, num_paulis)
        sign_change_indexes = random.choices(
            range(num_paulis), k=num_invalid_signs)
        sign_changes = random.choices(invalid_signs, k=num_invalid_signs)
        for index, sign in zip(sign_change_indexes, sign_changes):
            paulis[index].letter.sign = sign

        with pytest.raises(ValueError):
            _ = Check(paulis)


def test_check_fails_if_any_pauli_has_letter_I():
    # TODO - remove this in future and make SyndromeExtractor handle it
    #  gracefully.
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randrange(1, 10)
        max_paulis = random.randrange(1, 100)
        num_paulis = min(
            max_paulis, default_max_unique_sample_size(dimension))
        paulis = unique_random_sign_1_paulis_tuple_coords_int(
            num_paulis, dimension)

        # Pick at least one Pauli to put an identity letter on.
        num_identities = random.randint(1, num_paulis)
        identity_indexes = random.choices(
            range(num_paulis), k=num_identities)
        for i in identity_indexes:
            paulis[i].letter.letter = 'I'

        with pytest.raises(ValueError):
            _ = Check(paulis)


def test_check_fails_if_pauli_dict_given_but_no_anchor():
    repeats = default_test_repeats_small
    for _ in range(repeats):
        dimension = random.randrange(1, 10)
        max_paulis = random.randrange(0, 100)
        num_paulis = min(
            max_paulis, default_max_unique_sample_size(dimension))
        paulis = unique_random_xyz_sign_1_paulis_tuple_coords_int(
            num_paulis, dimension)
        paulis_dict = {pauli.qubit.coords: pauli for pauli in paulis}

        with pytest.raises(ValueError):
            _ = Check(paulis_dict, anchor=None)


def test_check_creates_right_offsets_if_coords_tuples():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randrange(1, 10)
        max_paulis = random.randrange(1, 100)
        num_paulis = min(
            max_paulis, default_max_unique_sample_size(dimension))
        paulis = unique_random_xyz_sign_1_paulis_tuple_coords_int(
            num_paulis, dimension)
        anchor = random_tuple_coords_int(dimension)
        offsets = [
            tuple([a-b for a, b in zip(pauli.qubit.coords, anchor)])
            for pauli in paulis]
        expected_paulis = {
            offset: pauli for offset, pauli in zip(offsets, paulis)}

        check = Check(paulis, anchor)
        assert check.paulis == expected_paulis


def test_check_creates_right_offsets_if_coords_non_tuples():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        max_paulis = random.randrange(1, 100)
        num_paulis = min(
            max_paulis, default_max_unique_sample_size(1))
        paulis = unique_random_xyz_sign_1_paulis_non_tuple_coords_int(
            num_paulis)
        anchor = random_non_tuple_coords_int()
        offsets = [
            pauli.qubit.coords - anchor
            for pauli in paulis]
        expected_paulis = {
            offset: pauli for offset, pauli in zip(offsets, paulis)}

        check = Check(paulis, anchor)
        assert check.paulis == expected_paulis


def test_check_defaults_to_right_anchor_when_coords_are_tuples():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randrange(1, 10)
        max_qubits = random.randrange(1, 100)
        num_qubits = min(
            max_qubits, default_max_unique_sample_size(dimension))
        paulis = unique_random_xyz_sign_1_paulis_tuple_coords_int(
            num_qubits, dimension)

        coords = [pauli.qubit.coords for pauli in paulis]
        midpoint = tuple(map(mean, zip(*coords)))

        check = Check(paulis, anchor=None)
        assert check.anchor == midpoint


def test_check_defaults_to_right_anchor_when_coords_are_non_tuples():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        max_qubits = random.randrange(1, 100)
        num_qubits = min(
            max_qubits, default_max_unique_sample_size(1))
        paulis = unique_random_xyz_sign_1_paulis_non_tuple_coords_int(
            num_qubits)

        coords = [pauli.qubit.coords for pauli in paulis]
        midpoint = mean(coords)

        check = Check(paulis, anchor=None)
        assert check.anchor == midpoint


def test_check_fails_if_pauli_dimensions_vary():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        max_dimension = random.randrange(1, 10)
        max_qubits = random.randrange(1, 100)
        num_qubits = min(
            max_qubits, default_max_unique_sample_size(max_dimension))
        paulis = unique_random_xyz_sign_1_paulis_tuple_coords_int_varying_dims(
            num_qubits, max_dimension)

        dimensions = {len(pauli.qubit.coords) for pauli in paulis}
        if len(dimensions) > 1:
            # Test if it fails when passing in a list...
            with pytest.raises(ValueError):
                _ = Check(paulis)
            # ... and also when passing in a dict
            anchor = (0,)
            pauli_dict = {pauli.qubit.coords: pauli for pauli in paulis}
            with pytest.raises(ValueError):
                _ = Check(pauli_dict, anchor)


def test_check_fails_if_some_pauli_coords_are_tuples_and_some_are_not():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        # Need at least two qubits here.
        max_qubits = random.randrange(2, 100)
        num_qubits = min(
            max_qubits, default_max_unique_sample_size(1))
        tuple_paulis = unique_random_xyz_sign_1_paulis_tuple_coords_int(
            num_qubits // 2, 1)

        non_tuple_paulis = unique_random_xyz_sign_1_paulis_non_tuple_coords_int(
            (num_qubits + 1) // 2)

        paulis = tuple_paulis + non_tuple_paulis
        # Test if it fails when passing in a list...
        with pytest.raises(ValueError):
            _ = Check(paulis)
        # ... and also when passing in a dict
        anchor = (0,)
        pauli_dict = {pauli.qubit.coords: pauli for pauli in paulis}
        with pytest.raises(ValueError):
            _ = Check(pauli_dict, anchor)


def test_check_fails_if_offsets_dimensions_vary():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randrange(1, 10)
        max_qubits = random.randrange(1, 100)
        num_qubits = min(
            max_qubits, default_max_unique_sample_size(dimension))
        paulis = unique_random_xyz_sign_1_paulis_tuple_coords_int(
            num_qubits, dimension)
        offsets = unique_random_tuple_coords_int_varying_dims(
            num_qubits, dimension)
        dimensions = {coords_length(offset) for offset in offsets}
        if len(dimensions) > 1:
            pauli_dict = {
                offset: pauli for offset, pauli in zip(offsets, paulis)}
            anchor = tuple(0 for _ in range(dimension))
            with pytest.raises(ValueError):
                _ = Check(pauli_dict, anchor)


def test_check_fails_if_some_offsets_are_tuples_and_some_are_not():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = 1
        # Need max_qubits to be at least two here
        max_qubits = random.randrange(2, 100)
        num_qubits = min(
            max_qubits, default_max_unique_sample_size(dimension))
        paulis = unique_random_xyz_sign_1_paulis_tuple_coords_int(
            num_qubits, dimension)
        tuple_offsets = unique_random_tuple_coords_int(
            num_qubits // 2, dimension)
        non_tuple_offsets = unique_random_non_tuple_coords_int(
            (num_qubits + 1) // 2)
        offsets = tuple_offsets + non_tuple_offsets

        pauli_dict = {
            offset: pauli for offset, pauli in zip(offsets, paulis)}
        anchor = tuple(0 for _ in range(dimension))
        with pytest.raises(ValueError):
            _ = Check(pauli_dict, anchor)


def test_check_fails_if_anchor_and_pauli_dims_differ():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        [anchor_dim, pauli_dim] = random.sample(range(1, 10), k=2)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        anchor = random_tuple_coords_int(anchor_dim)
        paulis = unique_random_xyz_sign_1_paulis_tuple_coords_int(
            num_paulis, pauli_dim)

        # Test if it fails when passing in a list...
        with pytest.raises(ValueError):
            _ = Check(paulis, anchor)
        # ... and also when passing in a dict
        pauli_dict = {pauli.qubit.coords: pauli for pauli in paulis}
        with pytest.raises(ValueError):
            _ = Check(pauli_dict, anchor)


def test_check_fails_if_anchor_non_tuple_but_pauli_coords_tuples():
    repeats = default_test_repeats_small
    for _ in range(repeats):
        anchor = random_non_tuple_coords_int()
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        paulis = unique_random_xyz_sign_1_paulis_tuple_coords_int(
            num_paulis, 1)

        # Test if it fails when passing in a list...
        with pytest.raises(ValueError):
            _ = Check(paulis, anchor)
        # ... and also when passing in a dict
        pauli_dict = {pauli.qubit.coords: pauli for pauli in paulis}
        with pytest.raises(ValueError):
            _ = Check(pauli_dict, anchor)


def test_check_fails_if_anchor_tuple_but_pauli_coords_non_tuples():
    repeats = default_test_repeats_small
    for _ in range(repeats):
        anchor = random_tuple_coords_int(1)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        paulis = unique_random_xyz_sign_1_paulis_non_tuple_coords_int(
            num_paulis)

        # Test if it fails when passing in a list...
        with pytest.raises(ValueError):
            _ = Check(paulis, anchor)
        # ... and also when passing in a dict
        pauli_dict = {pauli.qubit.coords: pauli for pauli in paulis}
        with pytest.raises(ValueError):
            _ = Check(pauli_dict, anchor)


def test_check_fails_if_anchor_and_offset_dims_differ():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        [anchor_and_pauli_dim, offsets_dim] = random.sample(range(1, 10), k=2)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        anchor = random_tuple_coords_int(anchor_and_pauli_dim)
        paulis = unique_random_xyz_sign_1_paulis_tuple_coords_int(
            num_paulis, anchor_and_pauli_dim)
        offsets = unique_random_tuple_coords_int(
            num_paulis, offsets_dim)
        pauli_dict = {offset: pauli for offset, pauli in zip(offsets, paulis)}

        with pytest.raises(ValueError):
            _ = Check(pauli_dict, anchor)


def test_check_fails_if_anchor_non_tuple_but_offset_coords_tuples():
    repeats = default_test_repeats_small
    for _ in range(repeats):
        anchor = random_non_tuple_coords_int()
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        paulis = unique_random_xyz_sign_1_paulis_non_tuple_coords_int(
            num_paulis)
        offsets = unique_random_tuple_coords_int(num_paulis, 1)
        pauli_dict = {offset: pauli for offset, pauli in zip(offsets, paulis)}

        with pytest.raises(ValueError):
            _ = Check(pauli_dict, anchor)


def test_check_fails_if_anchor_tuple_but_offset_coords_non_tuples():
    repeats = default_test_repeats_small
    for _ in range(repeats):
        anchor = random_tuple_coords_int(1)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        paulis = unique_random_xyz_sign_1_paulis_tuple_coords_int(
            num_paulis, 1)
        offsets = unique_random_non_tuple_coords_int(num_paulis)
        pauli_dict = {offset: pauli for offset, pauli in zip(offsets, paulis)}

        with pytest.raises(ValueError):
            _ = Check(pauli_dict, anchor)


def test_check_dimension_when_coords_tuples():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(dimension))
        paulis = unique_random_xyz_sign_1_paulis_tuple_coords_int(
            num_paulis, dimension)
        check = Check(paulis)
        assert check.dimension == dimension


def test_check_dimension_when_coords_non_tuples():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        paulis = unique_random_xyz_sign_1_paulis_non_tuple_coords_int(
            num_paulis)
        check = Check(paulis)
        assert check.dimension == 1


def test_check_weight():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(dimension))
        paulis = unique_random_xyz_sign_1_paulis_tuple_coords_int(
            num_paulis, dimension)
        check = Check(paulis)
        assert check.weight == num_paulis


def test_check_colour():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(dimension))
        paulis = unique_random_xyz_sign_1_paulis_tuple_coords_int(
            num_paulis, dimension)
        colour = random_colour()
        check = Check(paulis, colour=colour)
        assert check.colour == colour


# X test no qubit used more than once
# test pauli dict is created properly, i.e.
#   X if dict given, anchor given too
#   X if list given, check offsets are what's expected
# X test sign is 1
# test dimensions:
#   X if dict given, check keys, paulis and anchor have same dimension
#   X test all paulis in same dimension
#   X test paulis and anchor have same dimension
# test all attributes
#   X weight
#   X colour
#   X dimension
#   X anchor
# X behaviour if no paulis passed in? Fail?


import random
from statistics import mean

import pytest

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliY, PauliX, PauliLetter
from tests.utils.colours import random_colour
from tests.utils.coordinates import random_coords, random_coordss, coords_length
from tests.utils.numbers import default_max_unique_sample_size, default_test_repeats_medium, default_test_repeats_small
from tests.utils.paulis import random_paulis, random_grouped_paulis


def test_check_fails_if_no_paulis_given():
    expected_error = "Can't create a check from an empty list or dict"
    with pytest.raises(ValueError, match=expected_error):
        _ = Check([])
    with pytest.raises(ValueError, match=expected_error):
        _ = Check({})


def test_check_fails_if_qubit_used_more_than_once():
    repeats = default_test_repeats_medium
    expected_error = "Can't include the same qubit more than once"
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        # Use 1 as min because the test is about whether a qubit is used more
        # than once. Doesn't need to cover the case where there's no qubits.
        max_qubits = random.randint(1, 100)
        max_qubits = min(max_qubits, default_max_unique_sample_size(dimension))
        # Guarantee that we choose more letters than qubits.
        num_paulis = random.randint(max_qubits + 1, 3 * max_qubits)

        grouped_paulis = random_grouped_paulis(
            max_qubits,
            num_paulis,
            int_coords=True,
            dimension=dimension,
            from_signs=[1, -1])
        paulis = [
            pauli
            for _, paulis in grouped_paulis.items()
            for pauli in paulis]

        with pytest.raises(ValueError, match=expected_error):
            _ = Check(paulis)


# def test_check_fails_if_not_all_paulis_have_sign_1():
#     # TODO - allow -1 signs too in future.
#     invalid_signs = [1j, -1, -1j]
#     repeats = default_test_repeats_medium
#     expected_error = "All Paulis in a check must have sign 1"
#     for _ in range(repeats):
#         dimension = random.randrange(1, 10)
#         max_paulis = random.randrange(1, 100)
#         num_paulis = min(
#             max_paulis, default_max_unique_sample_size(dimension))
#         paulis = random_paulis(
#             num_paulis,
#             unique_qubits=True,
#             int_coords=True,
#             dimension=dimension,
#             from_letters=['X', 'Y', 'Z'])
#
#         # Pick at least one Pauli to put an invalid sign on.
#         num_invalid_signs = random.randint(1, num_paulis)
#         sign_change_indexes = random.choices(
#             range(num_paulis), k=num_invalid_signs)
#         sign_changes = random.choices(invalid_signs, k=num_invalid_signs)
#         for index, sign in zip(sign_change_indexes, sign_changes):
#             paulis[index].letter.sign = sign
#
#         with pytest.raises(ValueError, match=expected_error):
#             _ = Check(paulis)


# def test_check_fails_if_any_pauli_has_letter_I():
#     # TODO - remove this in future and make SyndromeExtractor handle it
#     #  gracefully.
#     repeats = default_test_repeats_medium
#     expected_error = "Paulis with letter I aren't allowed in a Check"
#     for _ in range(repeats):
#         dimension = random.randrange(1, 10)
#         max_paulis = random.randrange(1, 100)
#         num_paulis = min(
#             max_paulis, default_max_unique_sample_size(dimension))
#         paulis = random_paulis(
#             num_paulis,
#             unique_qubits=True,
#             int_coords=True,
#             dimension=dimension,
#             from_signs=[1, -1])
#
#         # Pick at least one Pauli to put an identity letter on.
#         num_identities = random.randint(1, num_paulis)
#         identity_indexes = random.choices(
#             range(num_paulis), k=num_identities)
#         for i in identity_indexes:
#             paulis[i].letter.letter = 'I'
#
#         with pytest.raises(ValueError, match=expected_error):
#             _ = Check(paulis)


def test_check_fails_if_pauli_dict_given_but_no_anchor():
    repeats = default_test_repeats_small
    expected_error = \
        "If dictionary of Paulis is supplied, `anchor` mustn't be None"
    for _ in range(repeats):
        dimension = random.randrange(1, 10)
        max_paulis = random.randrange(1, 100)
        num_paulis = min(
            max_paulis, default_max_unique_sample_size(dimension))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            dimension=dimension,
            from_signs=[1, -1])
        paulis_dict = {pauli.qubit.coords: pauli for pauli in paulis}

        with pytest.raises(ValueError, match=expected_error):
            _ = Check(paulis_dict, anchor=None)


def test_check_creates_right_offsets_if_coords_tuples():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randrange(1, 10)
        max_paulis = random.randrange(1, 100)
        num_paulis = min(
            max_paulis, default_max_unique_sample_size(dimension))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            dimension=dimension,
            from_signs=[1, -1])
        anchor = random_coords(int_coords=True, dimension=dimension)
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
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            tuple_coords=False,
            from_signs=[1, -1])
        anchor = random_coords(int_coords=True, tuple_coords=False)
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
        max_paulis = random.randrange(1, 100)
        num_paulis = min(
            max_paulis, default_max_unique_sample_size(dimension))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            dimension=dimension,
            from_signs=[1, -1])

        coords = [pauli.qubit.coords for pauli in paulis]
        midpoint = tuple(map(mean, zip(*coords)))

        check = Check(paulis, anchor=None)
        assert check.anchor == midpoint


def test_check_defaults_to_right_anchor_when_coords_are_non_tuples():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        max_paulis = random.randrange(1, 100)
        num_paulis = min(
            max_paulis, default_max_unique_sample_size(1))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            tuple_coords=False,
            from_signs=[1, -1])

        coords = [pauli.qubit.coords for pauli in paulis]
        midpoint = mean(coords)

        check = Check(paulis, anchor=None)
        assert check.anchor == midpoint


def test_check_fails_if_pauli_dimensions_vary():
    repeats = default_test_repeats_medium
    expected_error = "Paulis within a check must all have the same dimension"
    for _ in range(repeats):
        # Need at least two dimensions and two checks if the dimensions are
        # going to differ
        max_dimension = random.randrange(2, 10)
        max_paulis = random.randrange(2, 100)
        num_paulis = min(
            max_paulis, default_max_unique_sample_size(max_dimension))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            max_dimension=max_dimension,
            from_signs=[1, -1])

        dimensions = {len(pauli.qubit.coords) for pauli in paulis}
        if len(dimensions) > 1:
            # Test if it fails when passing in a list...
            with pytest.raises(ValueError, match=expected_error):
                _ = Check(paulis)
            # ... and also when passing in a dict
            anchor = (0,)
            pauli_dict = {pauli.qubit.coords: pauli for pauli in paulis}
            with pytest.raises(ValueError, match=expected_error):
                _ = Check(pauli_dict, anchor)


def test_check_fails_if_some_pauli_coords_are_tuples_and_some_are_not():
    repeats = default_test_repeats_medium
    expected_error = "Can't mix tuple and non-tuple coordinates"
    for _ in range(repeats):
        # Need at least two paulis here, with tuple coordinates.
        max_paulis = random.randrange(2, 50)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            dimension=1,
            from_signs=[1, -1])

        # Pick at least one but not all the paulis and turn their
        # coordinates into a non-tuple.
        num_non_tuple_paulis = random.randint(1, num_paulis - 1)
        non_tuple_pauli_indexes = random.sample(
            range(num_paulis), k=num_non_tuple_paulis)
        for i in non_tuple_pauli_indexes:
            paulis[i].qubit.coords = paulis[i].qubit.coords[0]

        # Test if it fails when passing in a list...
        with pytest.raises(ValueError, match=expected_error):
            _ = Check(paulis)
        # ... and also when passing in a dict
        anchor = (0,)
        pauli_dict = {pauli.qubit.coords: pauli for pauli in paulis}
        with pytest.raises(ValueError, match=expected_error):
            _ = Check(pauli_dict, anchor)


def test_check_fails_if_offsets_dimensions_vary():
    repeats = default_test_repeats_medium
    expected_error = \
        "The given distances from the check's anchor to the Paulis must all " \
        "have the same dimensions"
    for _ in range(repeats):
        dimension = random.randrange(1, 10)
        max_paulis = random.randrange(1, 100)
        num_paulis = min(
            max_paulis, default_max_unique_sample_size(dimension))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            dimension=dimension,
            from_signs=[1, -1])
        offsets = random_coordss(
            num_paulis,
            unique=True,
            int_coords=True,
            max_dimension=dimension)
        dimensions = {coords_length(offset) for offset in offsets}
        if len(dimensions) > 1:
            pauli_dict = {
                offset: pauli for offset, pauli in zip(offsets, paulis)}
            anchor = tuple(0 for _ in range(dimension))
            with pytest.raises(ValueError, match=expected_error):
                _ = Check(pauli_dict, anchor)


def test_check_fails_if_some_offsets_are_tuples_and_some_are_not():
    repeats = default_test_repeats_medium
    expected_error = "Can't mix tuple and non-tuple offsets"
    for _ in range(repeats):
        # Need at least two paulis here, with tuple coordinates.
        max_paulis = random.randrange(2, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            dimension=1,
            from_signs=[1, -1])
        offsets = random_coordss(
            num_paulis,
            unique=True,
            int_coords=True,
            dimension=1)

        # Pick at least one but not all the paulis and turn their
        # coordinates into a non-tuple.
        num_non_tuple_offsets = random.randint(1, num_paulis - 1)
        non_tuple_offset_indexes = random.sample(
            range(num_paulis), k=num_non_tuple_offsets)
        for i in non_tuple_offset_indexes:
            offsets[i] = offsets[i][0]

        anchor = (0,)
        pauli_dict = {
            offset: pauli for offset, pauli in zip(offsets, paulis)}
        with pytest.raises(ValueError, match=expected_error):
            _ = Check(pauli_dict, anchor)


def test_check_fails_if_anchor_and_pauli_dims_differ():
    repeats = default_test_repeats_medium
    expected_error = "Anchor must have same dimensions as Paulis"
    for _ in range(repeats):
        [anchor_dim, pauli_dim] = random.sample(range(1, 10), k=2)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        anchor = random_coords(int_coords=True, dimension=anchor_dim)
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            dimension=pauli_dim,
            from_signs=[1, -1])

        # Test if it fails when passing in a list...
        with pytest.raises(ValueError, match=expected_error):
            _ = Check(paulis, anchor)
        # ... and also when passing in a dict
        pauli_dict = {pauli.qubit.coords: pauli for pauli in paulis}
        with pytest.raises(ValueError, match=expected_error):
            _ = Check(pauli_dict, anchor)


def test_check_fails_if_anchor_non_tuple_but_pauli_coords_tuples():
    repeats = default_test_repeats_small
    expected_error = \
        "Anchor and Pauli coordinates must all be tuples or all be non-tuples"
    for _ in range(repeats):
        anchor = random_coords(int_coords=True, tuple_coords=False)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            dimension=1,
            from_signs=[1, -1])

        # Test if it fails when passing in a list...
        with pytest.raises(ValueError, match=expected_error):
            _ = Check(paulis, anchor)
        # ... and also when passing in a dict
        pauli_dict = {pauli.qubit.coords: pauli for pauli in paulis}
        with pytest.raises(ValueError, match=expected_error):
            _ = Check(pauli_dict, anchor)


def test_check_fails_if_anchor_tuple_but_pauli_coords_non_tuples():
    repeats = default_test_repeats_small
    expected_error = \
        "Anchor and Pauli coordinates must all be tuples or all be non-tuples"
    for _ in range(repeats):
        anchor = random_coords(int_coords=True, dimension=1)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            tuple_coords=False,
            from_signs=[1, -1])

        # Test if it fails when passing in a list...
        with pytest.raises(ValueError, match=expected_error):
            _ = Check(paulis, anchor)
        # ... and also when passing in a dict
        pauli_dict = {pauli.qubit.coords: pauli for pauli in paulis}
        with pytest.raises(ValueError, match=expected_error):
            _ = Check(pauli_dict, anchor)


def test_check_fails_if_anchor_and_offset_dims_differ():
    repeats = default_test_repeats_medium
    expected_error = "Anchor must have same dimensions as offsets"
    for _ in range(repeats):
        [anchor_and_pauli_dim, offsets_dim] = random.sample(range(1, 10), k=2)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        anchor = random_coords(int_coords=True, dimension=anchor_and_pauli_dim)
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            dimension=anchor_and_pauli_dim,
            from_signs=[1, -1])
        offsets = random_coordss(
            num_paulis,
            unique=True,
            int_coords=True,
            dimension=offsets_dim)
        pauli_dict = {offset: pauli for offset, pauli in zip(offsets, paulis)}

        with pytest.raises(ValueError, match=expected_error):
            _ = Check(pauli_dict, anchor)


def test_check_fails_if_anchor_non_tuple_but_offset_coords_tuples():
    repeats = default_test_repeats_small
    expected_error = \
        "Anchor and offsets must all be tuples or all be non-tuples"
    for _ in range(repeats):
        anchor = random_coords(int_coords=True, tuple_coords=False)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            tuple_coords=False,
            from_signs=[1, -1])
        offsets = random_coordss(
            num_paulis,
            unique=True,
            int_coords=True,
            dimension=1)
        pauli_dict = {offset: pauli for offset, pauli in zip(offsets, paulis)}

        with pytest.raises(ValueError, match=expected_error):
            _ = Check(pauli_dict, anchor)


def test_check_fails_if_anchor_tuple_but_offset_coords_non_tuples():
    repeats = default_test_repeats_small
    expected_error = \
        "Anchor and offsets must all be tuples or all be non-tuples"
    for _ in range(repeats):
        anchor = random_coords(int_coords=True, dimension=1)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            dimension=1,
            from_signs=[1, -1])
        offsets = random_coordss(
            num_paulis,
            unique=True,
            int_coords=True,
            tuple_coords=False)
        pauli_dict = {offset: pauli for offset, pauli in zip(offsets, paulis)}

        with pytest.raises(ValueError, match=expected_error):
            _ = Check(pauli_dict, anchor)


def test_check_fails_if_is_not_hermitian():
    expected_error = 'The product of all Paulis in a Check must be Hermitian'
    for _ in range(default_test_repeats_medium):
        dimension = random.randint(1, 10)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(dimension))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            dimension=dimension)
        num_imaginary_signs = len([
            pauli for pauli in paulis
            if pauli.letter.sign in [1j, -1j]])
        expect_non_hermitian = num_imaginary_signs % 2 == 1
        if expect_non_hermitian:
            with pytest.raises(ValueError, match=expected_error):
                _ = Check(paulis)
        else:
            # No error should be raised
            _ = Check(paulis)


def test_check_dimension_when_coords_tuples():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(dimension))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            dimension=dimension,
            from_signs=[1, -1])
        check = Check(paulis)
        assert check.dimension == dimension


def test_check_dimension_when_coords_non_tuples():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            tuple_coords=False,
            from_signs=[1, -1])
        check = Check(paulis)
        assert check.dimension == 1


def test_check_weight():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(dimension))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            dimension=dimension,
            from_signs=[1, -1])
        check = Check(paulis)
        assert check.weight == num_paulis


def test_check_colour():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(dimension))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            dimension=dimension,
            from_signs=[1, -1])
        colour = random_colour()
        check = Check(paulis, colour=colour)
        assert check.colour == colour


def test_check_has_tuple_coords_when_should_be_true():
    for _ in range(default_test_repeats_small):
        dimension = random.randint(1, 10)
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(dimension))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            dimension=dimension,
            from_signs=[1, -1])
        check = Check(paulis)
        assert check.has_tuple_coords


def test_check_has_tuple_coords_when_should_be_false():
    for _ in range(default_test_repeats_small):
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            tuple_coords=False,
            from_signs=[1, -1])
        check = Check(paulis)
        assert not check.has_tuple_coords


def test_check_repr():
    # Explicit example:
    paulis = [Pauli(Qubit(0), PauliX), Pauli(Qubit(1), PauliY)]
    check = Check(paulis, anchor=0)
    expected = {
        'product.word': {'word': 'XY', 'sign': 1},
        'anchor': 0,
        'colour': None,
        'paulis': {0: paulis[0], 1: paulis[1]}}
    assert str(check) == str(expected)


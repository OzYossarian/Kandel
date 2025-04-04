import random

import pytest

from main.building_blocks.Qubit import Qubit
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from tests.utils.utils_numbers import default_test_repeats_small, default_max_unique_sample_size, default_test_repeats_medium
from tests.building_blocks.pauli.utils_paulis import random_paulis, random_grouped_paulis


def test_logical_operator_fails_if_qubits_not_unique():
    expected_error = "Can't include the same qubit more than once"

    # Explicit test:
    qubit = Qubit(0)
    paulis = [
        Pauli(qubit, PauliLetter('X')),
        Pauli(qubit, PauliLetter('Y'))]
    with pytest.raises(ValueError, match=expected_error):
        LogicalOperator(paulis)

    # Random tests:
    for _ in range(default_test_repeats_medium):
        dimension = random.randint(1, 10)
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
        # Now flatten into a list of Paulis.
        paulis = [
            pauli
            for _, paulis in grouped_paulis.items()
            for pauli in paulis]

        with pytest.raises(ValueError, match=expected_error):
            LogicalOperator(paulis)


def test_logical_operator_fails_if_coords_dims_unequal():
    expected_error = \
        "Paulis within a logical operator must all have the same dimension"

    # Explicit test:
    paulis = [
        Pauli(Qubit((0, 0)), PauliLetter('X')),
        Pauli(Qubit((0, 0, 0)), PauliLetter('Y'))]
    with pytest.raises(ValueError, match=expected_error):
        LogicalOperator(paulis)

    # Random tests:
    for _ in range(default_test_repeats_small):
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
            with pytest.raises(ValueError, match=expected_error):
                LogicalOperator(paulis)


def test_logical_operator_fails_if_coords_types_unequal():
    expected_error = "Can't mix tuple and non-tuple coordinates"

    # Explicit test:
    paulis = [
        Pauli(Qubit((0,)), PauliLetter('X')),
        Pauli(Qubit(0), PauliLetter('Y'))]
    with pytest.raises(ValueError, match=expected_error):
        LogicalOperator(paulis)

    # Random test:
    for _ in range(default_test_repeats_small):
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

        with pytest.raises(ValueError, match=expected_error):
            LogicalOperator(paulis)


def test_logical_operator_fails_if_paulis_not_hermitian():
    expected_error = \
        "The product of all Paulis in a logical operator must be Hermitian"

    # Explicit test:
    paulis = [
        Pauli(Qubit(0), PauliLetter('X', 1j))]
    with pytest.raises(ValueError, match=expected_error):
        LogicalOperator(paulis)

    # Random tests:
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
                LogicalOperator(paulis)
        else:
            # No error should be raised
            LogicalOperator(paulis)


def test_logical_operator_at_round():
    # Explicit test:
    paulis = [
        Pauli(Qubit(0), PauliLetter('X')),
        Pauli(Qubit(1), PauliLetter('Y')),
        Pauli(Qubit(2), PauliLetter('Z'))]
    operator = LogicalOperator(paulis)
    for round in range(-10, 10):
        assert operator.at_round(round) == paulis

    # And random tests:
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
        operator = LogicalOperator(paulis)

        rounds = random.sample(range(-100, 100), k=default_test_repeats_small)
        for round in rounds:
            assert operator.at_round(round) == paulis


def test_logical_operator_update():
    # Explicit test:
    paulis = [
        Pauli(Qubit(0), PauliLetter('X')),
        Pauli(Qubit(1), PauliLetter('Y')),
        Pauli(Qubit(2), PauliLetter('Z'))]
    operator = LogicalOperator(paulis)
    for round in range(-10, 10):
        assert operator.update(round) == []

    # And random tests:
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
        operator = LogicalOperator(paulis)

        rounds = random.sample(range(-100, 100), k=default_test_repeats_small)
        for round in rounds:
            assert operator.update(round) == []


def test_logical_operator_dimension_and_has_tuple_coordinates_if_has_tuple_coordinates():
    # Explicit test:
    paulis = [
        Pauli(Qubit((0, 0)), PauliLetter('X')),
        Pauli(Qubit((1, 1)), PauliLetter('X'))]
    operator = LogicalOperator(paulis)
    assert operator.dimension == 2
    assert operator.has_tuple_coords

    # Random tests:
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
        operator = LogicalOperator(paulis)
        assert operator.has_tuple_coords
        assert operator.dimension == dimension


def test_logical_operator_dimension_and_has_tuple_coordinates_if_has_non_tuple_coordinates():
    # Explicit test:
    paulis = [
        Pauli(Qubit(0), PauliLetter('X')),
        Pauli(Qubit(1), PauliLetter('X'))]
    operator = LogicalOperator(paulis)
    assert operator.dimension == 1
    assert not operator.has_tuple_coords

    # Random tests:
    for _ in range(default_test_repeats_small):
        max_paulis = random.randint(1, 100)
        num_paulis = min(max_paulis, default_max_unique_sample_size(1))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            tuple_coords=False,
            from_signs=[1, -1])
        operator = LogicalOperator(paulis)
        assert operator.dimension == 1
        assert not operator.has_tuple_coords


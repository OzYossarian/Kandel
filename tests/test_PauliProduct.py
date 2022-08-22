import random
from functools import reduce
from operator import mul
from typing import Tuple

import pytest

from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.building_blocks.pauli.PauliWord import PauliWord
from tests.utils.numbers import default_max_unique_sample_size, default_test_repeats_medium, default_test_repeats_small
from tests.utils.paulis import random_grouped_paulis, compose_letters, random_paulis, valid_signs


class NotAPauliProduct:
    def __init__(self, _sorted_qubits: Tuple[Qubit], _sorted_word: PauliWord):
        self._sorted_qubits = _sorted_qubits
        self._sorted_word = _sorted_word


def test_pauli_product_word_and_weight_and_composition():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_qubits = random.randint(0, 100)
        max_qubits = min(max_qubits, default_max_unique_sample_size(dimension))
        num_paulis = random.randint(0, 3 * max_qubits)

        grouped_paulis = random_grouped_paulis(
            max_qubits, num_paulis, int_coords=True, dimension=dimension)
        # Flatten the grouped paulis
        paulis = [
            pauli
            for paulis in grouped_paulis.values()
            for pauli in paulis]
        product = PauliProduct(paulis)

        expected_paulis = [
            Pauli(qubit, compose_letters([pauli.letter for pauli in paulis]))
            for qubit, paulis in grouped_paulis.items()]
        expected_word = \
            ''.join([pauli.letter.letter for pauli in expected_paulis])
        expected_sign = \
            reduce(mul, [pauli.letter.sign for pauli in expected_paulis], 1)

        assert product.paulis == expected_paulis
        assert product.word.word == expected_word
        assert product.word.sign == expected_sign
        assert product.weight == len(expected_paulis)


def test_pauli_product_fails_when_pauli_dims_vary():
    repeats = default_test_repeats_medium
    expected_error = "Paulis within a check must all have the same dimension"
    for _ in range(repeats):
        max_dimension = random.randrange(1, 10)
        max_paulis = random.randrange(1, 100)
        num_paulis = min(
            max_paulis, default_max_unique_sample_size(max_dimension))
        paulis = random_paulis(
            num_paulis,
            unique_qubits=True,
            int_coords=True,
            max_dimension=max_dimension)

        dimensions = {len(pauli.qubit.coords) for pauli in paulis}
        if len(dimensions) > 1:
            with pytest.raises(ValueError, match=expected_error):
                _ = PauliProduct(paulis)


def test_pauli_product_fails_when_some_pauli_coords_are_tuple_and_some_are_not():
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
            dimension=1)

        # Pick at least one but not all the paulis and turn their
        # coordinates into a non-tuple.
        num_non_tuple_paulis = random.randint(1, num_paulis - 1)
        non_tuple_pauli_indexes = random.sample(
            range(num_paulis), k=num_non_tuple_paulis)
        for i in non_tuple_pauli_indexes:
            paulis[i].qubit.coords = paulis[i].qubit.coords[0]

        with pytest.raises(ValueError, match=expected_error):
            _ = PauliProduct(paulis)


def test_pauli_product_equality_when_grouped_paulis_are_permuted():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_qubits = random.randint(0, 100)
        max_qubits = min(max_qubits, default_max_unique_sample_size(dimension))
        num_paulis = random.randint(0, 3 * max_qubits)

        grouped_paulis = random_grouped_paulis(
            max_qubits, num_paulis, int_coords=True, dimension=dimension)
        # Convert it to a list so we can use shuffle.
        grouped_paulis = [
            (qubit, paulis) for qubit, paulis in grouped_paulis.items()]

        paulis = [pauli for _, paulis in grouped_paulis for pauli in paulis]
        product = PauliProduct(paulis)

        for _ in range(len(grouped_paulis)):
            random.shuffle(grouped_paulis)
            paulis = [pauli for _, paulis in grouped_paulis for pauli in paulis]
            shuffled = PauliProduct(paulis)
            assert product == shuffled


def test_pauli_product_equality():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_qubits = random.randint(0, 100)
        max_qubits = min(max_qubits, default_max_unique_sample_size(dimension))
        num_paulis = random.randint(0, 3 * max_qubits)

        grouped_paulis = random_grouped_paulis(
            max_qubits, num_paulis, int_coords=True, dimension=dimension)
        paulis = [
            pauli for
            _, paulis in grouped_paulis.items()
            for pauli in paulis]
        copied = paulis.copy()
        product_1 = PauliProduct(paulis)
        product_2 = PauliProduct(copied)
        assert product_1 == product_2


def test_pauli_product_inequality_when_data_are_different():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_qubits = random.randint(0, 100)
        max_qubits = min(max_qubits, default_max_unique_sample_size(dimension))
        num_paulis = random.randint(0, 3 * max_qubits)

        grouped_paulis_1 = random_grouped_paulis(
            max_qubits, num_paulis, int_coords=True, dimension=dimension)
        paulis_1 = [
            pauli
            for _, paulis in grouped_paulis_1.items()
            for pauli in paulis]

        grouped_paulis_2 = random_grouped_paulis(
            max_qubits, num_paulis, int_coords=True, dimension=dimension)
        paulis_2 = [
            pauli
            for _, paulis in grouped_paulis_2.items()
            for pauli in paulis]

        product_1 = PauliProduct(paulis_1)
        product_2 = PauliProduct(paulis_2)
        expect_unequal = \
            product_1._sorted_qubits != product_2._sorted_qubits or \
            product_1._sorted_word != product_2._sorted_word

        if expect_unequal:
            assert product_1 != product_2


def test_pauli_product_inequality_when_types_are_different():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_qubits = random.randint(0, 100)
        max_qubits = min(max_qubits, default_max_unique_sample_size(dimension))
        num_paulis = random.randint(0, 3 * max_qubits)

        grouped_paulis = random_grouped_paulis(
            max_qubits, num_paulis, int_coords=True, dimension=dimension)
        paulis = [
            pauli
            for _, paulis in grouped_paulis.items()
            for pauli in paulis]

        product = PauliProduct(paulis)
        not_a_product = NotAPauliProduct(
            product._sorted_qubits, product._sorted_word)

        assert product != not_a_product


def test_pauli_product_equal_up_to_sign():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_qubits = random.randint(0, 100)
        max_qubits = min(max_qubits, default_max_unique_sample_size(dimension))
        num_paulis = random.randint(0, 3 * max_qubits)

        grouped_paulis_1 = random_grouped_paulis(
            max_qubits, num_paulis, int_coords=True, dimension=dimension)
        paulis_1 = [
            pauli
            for _, paulis in grouped_paulis_1.items()
            for pauli in paulis]

        product_1 = PauliProduct(paulis_1)

        # Make a copy of these paulis
        paulis_2 = [Pauli(pauli.qubit, pauli.letter) for pauli in paulis_1]
        for _ in range(default_test_repeats_small):
            for pauli in paulis_2:
                pauli.letter.sign = random.choice(valid_signs)

            product_2 = PauliProduct(paulis_2)
            assert product_1.equal_up_to_sign(product_2)


def test_pauli_product_repr():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_qubits = random.randint(0, 100)
        max_qubits = min(max_qubits, default_max_unique_sample_size(dimension))
        num_paulis = random.randint(0, 3 * max_qubits)

        grouped_paulis = random_grouped_paulis(
            max_qubits, num_paulis, int_coords=True, dimension=dimension)
        paulis = [
            pauli
            for _, paulis in grouped_paulis.items()
            for pauli in paulis]
        product = PauliProduct(paulis)

        expected_paulis = [
            Pauli(qubit, compose_letters([pauli.letter for pauli in paulis]))
            for qubit, paulis in grouped_paulis.items()]
        expected_word = \
            ''.join([pauli.letter.letter for pauli in expected_paulis])
        expected_sign = \
            reduce(mul, [pauli.letter.sign for pauli in expected_paulis], 1)
        expected = {
            'word': PauliWord(expected_word, expected_sign),
            'paulis': expected_paulis}

        assert str(product) == str(expected)

import itertools
import random
from collections import Counter
from functools import reduce
from operator import mul
from typing import Iterable

import pytest

from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.pauli.utils import remove_identities, compose
from tests.utils.utils_numbers import default_max_unique_sample_size, default_test_repeats_medium
from tests.building_blocks.pauli.utils_paulis import random_grouped_paulis, random_paulis


def test_compose():
    # This is a difficult one to test without just reimplementing the
    # function here! Will make up for it with some specific examples.
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_qubits = random.randint(0, 100)
        num_qubits = min(max_qubits, default_max_unique_sample_size(dimension))
        num_paulis = random.randint(0, 3 * max_qubits)

        grouped_paulis = random_grouped_paulis(
            num_qubits, num_paulis, int_coords=True, dimension=dimension)
        # Flatten the grouped paulis
        paulis = [
            pauli
            for paulis in grouped_paulis.values()
            for pauli in paulis]

        def compose_letters(letters: Iterable[PauliLetter]):
            return reduce(lambda x, y: x.compose(y), letters)

        result = compose(paulis, identities_removed=False)
        expected = [
            Pauli(qubit, compose_letters([pauli.letter for pauli in paulis]))
            for qubit, paulis in grouped_paulis.items()]

        assert result == expected


def test_compose_XY_equals_iZ():
    n = 5
    qubits = [Qubit(i) for i in range(n)]
    for i in range(n):
        paulis = [
            Pauli(qubits[i], PauliLetter('X')),
            Pauli(qubits[i], PauliLetter('Y'))]
        result = compose(paulis, identities_removed=False)
        expected = [Pauli(qubits[i], PauliLetter('Z', sign=1j))]
        assert result == expected


def test_compose_XY_Z_equals_iZ_Z():
    n = 5
    qubits = [Qubit(i) for i in range(n)]
    for u, v in itertools.product(range(n), range(n)):
        # Only interested in distinct u, v.
        if u != v:
            paulis = [
                Pauli(qubits[u], PauliLetter('X')),
                Pauli(qubits[u], PauliLetter('Y')),
                Pauli(qubits[v], PauliLetter('Z'))]
            result = compose(paulis, identities_removed=False)
            expected = [
                Pauli(qubits[u], PauliLetter('Z', sign=1j)),
                Pauli(qubits[v], PauliLetter('Z', sign=1))]
            assert result == expected


def test_compose_XYZ_X_Y_equals_iZ_X_Y():
    n = 5
    qubits = [Qubit(i) for i in range(n)]
    for u, v, w in itertools.product(range(n), range(n), range(n)):
        # Only interested in distinct u, v, w.
        if len({u, v, w}) == 3:
            paulis = [
                Pauli(qubits[u], PauliLetter('X')),
                Pauli(qubits[u], PauliLetter('Y')),
                Pauli(qubits[u], PauliLetter('Z')),
                Pauli(qubits[v], PauliLetter('X')),
                Pauli(qubits[w], PauliLetter('Y'))]
            result = compose(paulis, identities_removed=False)
            expected = [
                Pauli(qubits[u], PauliLetter('I', sign=1j)),
                Pauli(qubits[v], PauliLetter('X', sign=1)),
                Pauli(qubits[w], PauliLetter('Y', sign=1))]
            assert result == expected


def test_compose_XYZ_XZY_iI_equals_iZ_minusiZ_I():
    n = 5
    qubits = [Qubit(i) for i in range(n)]
    for u, v, w in itertools.product(range(n), range(n), range(n)):
        # Only interested in distinct u, v, w.
        if len({u, v, w}) == 3:
            paulis = [
                Pauli(qubits[u], PauliLetter('X')),
                Pauli(qubits[u], PauliLetter('Y')),
                Pauli(qubits[u], PauliLetter('Z')),
                Pauli(qubits[v], PauliLetter('X')),
                Pauli(qubits[v], PauliLetter('Z')),
                Pauli(qubits[v], PauliLetter('Y')),
                Pauli(qubits[w], PauliLetter('I', sign=1j))]
            result = compose(paulis, identities_removed=False)
            expected = [
                Pauli(qubits[u], PauliLetter('I', sign=1j)),
                Pauli(qubits[v], PauliLetter('I', sign=-1j)),
                Pauli(qubits[w], PauliLetter('I', sign=1j))]
            assert result == expected


def test_remove_identities_when_identities_sign_1():
    # Explicit test:
    paulis = [
        Pauli(Qubit(0), PauliLetter('I')),
        Pauli(Qubit(1), PauliLetter('X'))]
    result = remove_identities(paulis)
    assert result == [paulis[1]]

    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        num_paulis = random.randint(0, 100)

        paulis = identities_sign = None
        # Repeat til we get identities with total sign 1. Happens 25% of the
        # time so this won't slow us down too much.
        while identities_sign != 1:
            paulis = random_paulis(num_paulis, int_coords=True, dimension=dimension)
            identities = [pauli for pauli in paulis if pauli.letter.letter == 'I']
            identities_signs = [pauli.letter.sign for pauli in identities]
            identities_sign = reduce(mul, identities_signs, 1)

        non_identities = [pauli for pauli in paulis if pauli.letter.letter != 'I']
        result = remove_identities(paulis)
        # Order irrelevant, so shouldn't compare lists. But can't compare
        # sets, because two Paulis acting via the same PauliLetter on the same
        # qubit are considered equal, so won't both appear in a set. So use a
        # Counter instead. (Could also sort the lists but that's longer)
        assert Counter(result) == Counter(non_identities)


def test_remove_identities_when_identities_sign_not_1_and_exist_non_identity_paulis():
    # Explicit test:
    qubits = [Qubit(0), Qubit(1)]
    paulis = [
        Pauli(qubits[0], PauliLetter('I', 1j)),
        Pauli(qubits[1], PauliLetter('X', 1))]
    result = remove_identities(paulis)
    assert result == [Pauli(qubits[1], PauliLetter('X', 1j))]

    # Random tests
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        num_identity_paulis = random.randint(1, 50)
        num_non_identity_paulis = random.randint(1, 50)

        identities = identities_sign = None
        # Repeat til we get identities with sign != 1. Happens 75% of the
        # time so this won't slow us down much.
        while identities_sign not in [1j, -1, -1j]:
            identities = random_paulis(
                num_identity_paulis,
                int_coords=True,
                dimension=dimension,
                from_letters=['I'])
            identities_signs = [pauli.letter.sign for pauli in identities]
            identities_sign = reduce(mul, identities_signs, 1)

        non_identities = random_paulis(
            num_non_identity_paulis,
            int_coords=True,
            dimension=dimension,
            from_letters=['X', 'Y', 'Z'])
        non_identities_signs = [pauli.letter.sign for pauli in non_identities]
        non_identities_sign = reduce(mul, non_identities_signs, 1)

        paulis = identities + non_identities
        result = remove_identities(paulis)
        # Order irrelevant, so shouldn't compare lists. But can't compare
        # sets, because two Paulis acting via the same PauliLetter on the same
        # qubit are considered equal, so won't both appear in a set. So use a
        # Counter instead. (Could also sort the lists but that's longer)
        assert Counter(result) == Counter(non_identities)
        # The identities' sign should have transferred onto the non-identities
        new_non_identities_signs = [pauli.letter.sign for pauli in non_identities]
        new_non_identities_sign = reduce(mul, new_non_identities_signs, 1)
        assert identities_sign * non_identities_sign == new_non_identities_sign


def test_remove_identities_fails_when_identities_sign_not_1_and_exist_no_non_identity_paulis():
    expected_error = \
        "Can't remove identities - they have a non-trivial sign and " \
        "there's no non-identity Paulis to transfer this sign onto"

    # Explicit test:
    qubits = [Qubit(0), Qubit(1)]
    paulis = [
        Pauli(qubits[0], PauliLetter('I', 1j)),
        Pauli(qubits[1], PauliLetter('I', 1))]
    with pytest.raises(ValueError, match=expected_error):
        remove_identities(paulis)

    # Random tests
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        num_identity_paulis = random.randint(1, 100)

        identities = identities_sign = None
        # Repeat til we get identities with sign != 1. Happens 75% of the
        # time so this won't slow us down much.
        while identities_sign not in [1j, -1, -1j]:
            identities = random_paulis(
                num_identity_paulis,
                int_coords=True,
                dimension=dimension,
                from_letters=['I'])
            identities_signs = [pauli.letter.sign for pauli in identities]
            identities_sign = reduce(mul, identities_signs, 1)

        with pytest.raises(ValueError, match=expected_error):
            remove_identities(identities)

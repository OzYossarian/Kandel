import itertools
import random
from collections import Counter
from functools import reduce
from operator import mul
from typing import List, Callable, Iterable

from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.pauli.utils import remove_identities, compose
from tests.utils.numbers import default_max_unique_sample_size, default_test_repeats_medium
from tests.utils.paulis import random_grouped_paulis_tuple_coords_int, random_paulis_tuple_coords_int, \
    random_xyz_paulis_tuple_coords_int


def test_compose():
    # This is a difficult one to test without just reimplementing the
    # function here! Will make up for it with some specific examples.
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_qubits = random.randint(0, 100)
        num_qubits = min(max_qubits, default_max_unique_sample_size(dimension))
        num_letters = random.randint(0, 3 * max_qubits)

        grouped_paulis = random_grouped_paulis_tuple_coords_int(
            num_qubits, num_letters, dimension)
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


def test_remove_identities_when_identities_sign_1_or_not_1():
    def get_expected(paulis: List[Pauli], identities_sign: int):
        if identities_sign == 1:
            return [pauli for pauli in paulis if pauli.letter.letter != 'I']
        else:
            return paulis

    return _test_remove_identities(
        random_paulis_tuple_coords_int, get_expected)


def test_remove_identities_when_no_identities_included():
    def get_expected(paulis: List[Pauli], identities_sign: int):
        # If no identity Paulis included, always expect to do nothing.
        return paulis
    return _test_remove_identities(
        random_xyz_paulis_tuple_coords_int, get_expected)


def _test_remove_identities(
        get_paulis: Callable[[int, int, int], List[Pauli]],
        get_expected: Callable[[List[Pauli], int], List[Pauli]]):
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        max_qubits = random.randint(0, 100)
        num_qubits = min(max_qubits, default_max_unique_sample_size(dimension))
        # Allow choosing more letters than there are qubits
        num_paulis = random.randint(0, 3 * num_qubits)
        paulis = get_paulis(num_qubits, num_paulis, dimension)

        identities = [pauli for pauli in paulis if pauli.letter.letter == 'I']
        identities_signs = [pauli.letter.sign for pauli in identities]
        identities_sign = reduce(mul, identities_signs, 1)
        result = remove_identities(paulis)
        expected = get_expected(paulis, identities_sign)

        # Order irrelevant, so shouldn't compare lists. But can't compare
        # sets, because two Paulis acting via the same PauliLetter on the same
        # qubit are considered equal, so won't both appear in a set. So use a
        # Counter instead. (Could also sort the lists but that's longer)
        assert Counter(result) == Counter(expected)

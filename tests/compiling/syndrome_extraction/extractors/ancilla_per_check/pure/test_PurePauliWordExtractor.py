import random

import pytest
from pytest_mock import MockerFixture

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.pure.PurePauliWordExtractor import \
    PurePauliWordExtractor
from tests.building_blocks.utils_checks import random_check
from tests.utils.utils_numbers import default_test_repeats_medium


def test_pure_pauli_word_extractor_get_ancilla_basis_fails_if_word_not_pure():
    expected_error = \
        "Can't use a PurePauliWordExtractor to extract syndrome of a check " \
        "whose product is not XX...X, YY...Y or ZZ...Z"
    extractor = PurePauliWordExtractor()

    # One explicit test:
    check = Check([
        Pauli(Qubit(0), PauliLetter('X')),
        Pauli(Qubit(1), PauliLetter('Y'))])
    with pytest.raises(ValueError, match=expected_error):
        extractor.get_ancilla_basis(check)

    # And some random tests
    def is_pure(check: Check):
        return all([
            pauli.letter == PauliLetter('X')
            for pauli in check.paulis.values()
        ]) or all([
            pauli.letter == PauliLetter('Y')
            for pauli in check.paulis.values()
        ]) or all([
            pauli.letter == PauliLetter('Z')
            for pauli in check.paulis.values()])

    for _ in range(default_test_repeats_medium):
        dimension = random.randint(1, 10)
        weight = random.randint(1, 10)
        check = random_check(
            int_coords=True, weight=weight, dimension=dimension)
        if not is_pure(check):
            with pytest.raises(ValueError, match=expected_error):
                extractor.get_ancilla_basis(check)


def test_pure_pauli_word_extractor_get_ancilla_basis_returns_right_basis(mocker: MockerFixture):
    x_word_ancilla_basis = mocker.Mock(spec=PauliLetter)
    y_word_ancilla_basis = mocker.Mock(spec=PauliLetter)
    z_word_ancilla_basis = mocker.Mock(spec=PauliLetter)
    extractor = PurePauliWordExtractor(
        x_word_ancilla_basis=x_word_ancilla_basis,
        y_word_ancilla_basis=y_word_ancilla_basis,
        z_word_ancilla_basis=z_word_ancilla_basis)

    x_check_weight = random.randint(1, 10)
    x_check_paulis = [
        Pauli(Qubit(i), PauliLetter('X')) for i in range(x_check_weight)]
    x_check = Check(x_check_paulis)

    y_check_weight = random.randint(1, 10)
    y_check_paulis = [
        Pauli(Qubit(i), PauliLetter('Y')) for i in range(y_check_weight)]
    y_check = Check(y_check_paulis)

    z_check_weight = random.randint(1, 10)
    z_check_paulis = [
        Pauli(Qubit(i), PauliLetter('Z')) for i in range(z_check_weight)]
    z_check = Check(z_check_paulis)

    assert extractor.get_ancilla_basis(x_check) == x_word_ancilla_basis
    assert extractor.get_ancilla_basis(y_check) == y_word_ancilla_basis
    assert extractor.get_ancilla_basis(z_check) == z_word_ancilla_basis

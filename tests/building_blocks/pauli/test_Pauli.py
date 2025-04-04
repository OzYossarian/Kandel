import random

from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from tests.utils.utils_numbers import default_test_repeats_medium, default_test_repeats_small
from tests.building_blocks.pauli.utils_paulis import random_pauli_letters, random_pauli_letter
from tests.building_blocks.utils_qubits import random_qubit, random_qubits


class NotAPauli:
    def __init__(self, qubit: Qubit, letter: PauliLetter):
        self.qubit = qubit
        self.letter = letter


def test_pauli_dimension_with_tuple_coords():
    repeats = default_test_repeats_small
    for _ in range(repeats):
        dimension = random.randint(1, 10)
        qubit = random_qubit(dimension=dimension)
        letter = random_pauli_letter()
        pauli = Pauli(qubit, letter)
        assert pauli.dimension == dimension


def test_pauli_dimension_with_non_tuple_coords():
    repeats = default_test_repeats_small
    for _ in range(repeats):
        qubit = random_qubit(tuple_coords=False)
        letter = random_pauli_letter()
        pauli = Pauli(qubit, letter)
        assert pauli.dimension == 1


def test_pauli_inequality_if_qubits_or_letters_differ():
    repeat = default_test_repeats_medium
    for _ in range(repeat):
        dimension = random.randint(1, 10)
        qubits = random_qubits(
            2, unique=True, dimension=dimension, int_coords=True)
        letters = random_pauli_letters(2)
        qubit_1, qubit_2 = tuple(qubits)
        letter_1, letter_2 = tuple(letters)
        pauli_1 = Pauli(qubit_1, letter_1)
        pauli_2 = Pauli(qubit_2, letter_2)

        if qubit_1 != qubit_2 or letter_1 != letter_2:
            assert pauli_1 != pauli_2


def test_pauli_inequality_if_one_is_not_a_pauli():
    repeat = default_test_repeats_medium
    for _ in range(repeat):
        dimension = random.randint(1, 10)
        qubit = random_qubit(int_coords=True, dimension=dimension)
        letter = random_pauli_letter()
        pauli = Pauli(qubit, letter)
        not_a_pauli = NotAPauli(qubit, letter)
        assert pauli != not_a_pauli


def test_pauli_equality_if_qubit_and_letters_equal():
    repeat = default_test_repeats_medium
    for _ in range(repeat):
        dimension = random.randint(1, 10)
        qubit = random_qubit(int_coords=True, dimension=dimension)
        letter = random_pauli_letter()
        pauli_1 = Pauli(qubit, letter)
        pauli_2 = Pauli(qubit, letter)
        assert pauli_1 == pauli_2


def test_pauli_repr():
    repeat = default_test_repeats_medium
    for _ in range(repeat):
        dimension = random.randint(1, 10)
        qubit = random_qubit(int_coords=True, dimension=dimension)
        letter = random_pauli_letter()
        pauli = Pauli(qubit, letter)
        expected = {
            'qubit': qubit,
            'letter': letter}
        assert str(pauli) == str(expected)


def test_pauli_has_tuple_coords():
    for _ in range(default_test_repeats_small):
        dimension = random.randint(1, 10)
        qubit = random_qubit(dimension=dimension)
        letter = random_pauli_letter()
        pauli = Pauli(qubit, letter)
        assert pauli.has_tuple_coords
    for _ in range(default_test_repeats_small):
        qubit = random_qubit(tuple_coords=False)
        letter = random_pauli_letter()
        pauli = Pauli(qubit, letter)
        assert not pauli.has_tuple_coords

import random

from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from tests.utils.paulis import random_pauli_letters, random_pauli_letter
from tests.utils.qubits import unique_random_qubits_tuple_coords_int, random_qubit_tuple_coords_int


class NotAPauli:
    def __init__(self, qubit: Qubit, letter: PauliLetter):
        self.qubit = qubit
        self.letter = letter


# Not much to test here, since Pauli is basically just a tuple containing a
# Qubit and PauliLetter
def test_pauli_inequality_if_qubits_or_letters_differ():
    repeat = 100
    for _ in range(repeat):
        dimension = random.randint(1, 10)
        qubits = unique_random_qubits_tuple_coords_int(2, dimension)
        letters = random_pauli_letters(2)
        qubit_1, qubit_2 = tuple(qubits)
        letter_1, letter_2 = tuple(letters)
        pauli_1 = Pauli(qubit_1, letter_1)
        pauli_2 = Pauli(qubit_2, letter_2)

        if qubit_1 != qubit_2 or letter_1 != letter_2:
            assert pauli_1 != pauli_2


def test_pauli_inequality_if_one_is_not_a_pauli():
    repeat = 100
    for _ in range(repeat):
        dimension = random.randint(1, 10)
        qubit = random_qubit_tuple_coords_int(dimension)
        letter = random_pauli_letter()
        pauli = Pauli(qubit, letter)
        not_a_pauli = NotAPauli(qubit, letter)
        assert pauli != not_a_pauli


def test_pauli_equality_if_qubit_and_letters_equal():
    repeat = 100
    for _ in range(repeat):
        dimension = random.randint(1, 10)
        qubit = random_qubit_tuple_coords_int(dimension)
        letter = random_pauli_letter()
        pauli_1 = Pauli(qubit, letter)
        pauli_2 = Pauli(qubit, letter)
        assert pauli_1 == pauli_2


def test_pauli_repr():
    repeat = 100
    for _ in range(repeat):
        dimension = random.randint(1, 10)
        qubit = random_qubit_tuple_coords_int(dimension)
        letter = random_pauli_letter()
        pauli = Pauli(qubit, letter)
        expected = {
            'qubit': qubit,
            'letter': letter}
        assert str(pauli) == str(expected)

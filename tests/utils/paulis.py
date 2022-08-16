import random

from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ, PauliY, PauliX, PauliLetter
from main.building_blocks.pauli.PauliWord import PauliWord
from tests.utils.numbers import default_max_coord, default_min_coord
from tests.utils.qubits import unique_random_qubits_tuple_coords, unique_random_qubits_tuple_coords_int

valid_letters = ['I', 'X', 'Y', 'Z']
valid_signs = [1, 0+1j, -1, 0-1j]
xyz = ['X', 'Y', 'Z']


def random_pauli_word(length: int):
    word = ''.join(random.choices(valid_letters, k=length))
    sign = random.choice(valid_signs)
    return PauliWord(word, sign)


def random_pauli_letter():
    letter = random.choice(valid_letters)
    sign = random.choice(valid_signs)
    return PauliLetter(letter, sign)


def random_pauli_letters(num: int):
    letters = random.choices(valid_letters, k=num)
    signs = random.choices(valid_signs, k=num)
    return [PauliLetter(letter, sign) for letter, sign in zip(letters, signs)]


def random_xyz_pauli_letter():
    letter = random.choice(xyz)
    sign = random.choice(valid_signs)
    return PauliLetter(letter, sign)


def random_xyz_pauli_letters(num: int):
    letters = random.choices(xyz, k=num)
    signs = random.choices(valid_signs, k=num)
    return [PauliLetter(letter, sign) for letter, sign in zip(letters, signs)]


def random_xyz_sign_1_pauli_letter():
    letter = random.choice(xyz)
    return PauliLetter(letter, 1)


def unique_random_xyz_sign_1_paulis_tuple_coords(
        num: int, dimension: int,
        min: float = default_min_coord, max: float = default_max_coord):
    qubits = unique_random_qubits_tuple_coords(num, dimension, min, max)
    letters = random.choices(xyz, k=num)
    paulis = [
        Pauli(qubit, PauliLetter(letter))
        for qubit, letter in zip(qubits, letters)]
    return paulis


def unique_random_paulis_tuple_coords_int(
        num: int, dimension: int,
        min: int = default_min_coord, max: int = default_max_coord):
    qubits = unique_random_qubits_tuple_coords_int(num, dimension, min, max)
    letters = random_pauli_letters(num)
    paulis = [
        Pauli(qubit, letter)
        for qubit, letter in zip(qubits, letters)]
    return paulis

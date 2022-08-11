import random

from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ, PauliY, PauliX, PauliLetter
from tests.utils.qubits import unique_random_qubits_tuple_coords


valid_letters = ['I', 'X', 'Y', 'Z']
valid_signs = [1, 0+1j, -1, 0-1j]
xyz_pauli_letters = [PauliX, PauliY, PauliZ]


def random_pauli_letter():
    letter = random.choice(valid_letters)
    sign = random.choice(valid_signs)
    return PauliLetter(letter, sign)


def random_pauli_letters(num: int):
    letters = random.choices(valid_letters, k=num)
    signs = random.choices(valid_signs, k=num)
    return [PauliLetter(letter, sign) for letter, sign in zip(letters, signs)]


def random_xyz_pauli_letter():
    return xyz_pauli_letters[random.randint(0, 2)]


def unique_random_xyz_paulis_tuple_coords(
        num: int, dimension: int, min: float = -10, max: float = 10):
    qubits = unique_random_qubits_tuple_coords(num, dimension, min, max)
    pauli_indexes = random.choices(range(3), k=num)
    pauli_letters = [xyz_pauli_letters[i] for i in pauli_indexes]
    paulis = [
        Pauli(qubit, letter)
        for qubit, letter in zip(qubits, pauli_letters)]
    return paulis

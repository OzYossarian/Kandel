import random
from functools import reduce
from typing import List, Iterable, Dict

from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.pauli.PauliWord import PauliWord
from tests.utils.utils_numbers import default_max_coord, default_min_coord
from tests.building_blocks.utils_qubits import random_qubits

valid_letters = ['I', 'X', 'Y', 'Z']
valid_signs = [1, 0+1j, -1, 0-1j]


def check_arguments(letters, signs):
    assert set(letters).issubset(valid_letters)
    assert set(signs).issubset(valid_signs)


def compose_letters(letters: Iterable[PauliLetter]):
    return reduce(lambda x, y: x.compose(y), letters)


def random_pauli_word(
        length: int,
        from_letters: List[str] = None,
        from_signs: List[complex] = None,
) -> PauliWord:
    if from_letters is None:
        from_letters = valid_letters
    if from_signs is None:
        from_signs = valid_signs
    check_arguments(from_letters, from_signs)

    word = ''.join(random.choices(from_letters, k=length))
    sign = random.choice(from_signs)
    return PauliWord(word, sign)


def random_pauli_letter(
        from_letters: List[str] = None,
        from_signs: List[complex] = None):
    return random_pauli_letters(1, from_letters, from_signs)[0]


def random_pauli_letters(
        num: int,
        from_letters: List[str] = None,
        from_signs: List[complex] = None,
) -> List[PauliLetter]:
    if from_letters is None:
        from_letters = valid_letters
    if from_signs is None:
        from_signs = valid_signs

    check_arguments(from_letters, from_signs)

    letters = random.choices(from_letters, k=num)
    signs = random.choices(from_signs, k=num)
    pauli_letters = [
        PauliLetter(letter, sign)
        for letter, sign in zip(letters, signs)]
    return pauli_letters


def random_paulis(
        num: int,
        unique_qubits: bool = False,
        int_coords: bool = False,
        tuple_coords: bool = True,
        dimension: int = None,
        max_dimension: int = None,
        from_letters: List[str] = None,
        from_signs: List[complex] = None,
        min_coord: int | float = default_min_coord,
        max_coord: int | float = default_max_coord,
) -> List[Pauli]:
    qubits = random_qubits(
        num,
        unique_qubits,
        int_coords,
        tuple_coords,
        dimension,
        max_dimension,
        min_coord,
        max_coord)
    letters = random_pauli_letters(
        num, from_letters, from_signs)
    paulis = [
        Pauli(qubit, letter)
        for qubit, letter in zip(qubits, letters)]

    return paulis


def random_pauli(
        int_coords: bool = False,
        tuple_coords: bool = True,
        dimension: int = None,
        max_dimension: int = None,
        from_letters: List[str] = None,
        from_signs: List[complex] = None,
        min_coord: int | float = default_min_coord,
        max_coord: int | float = default_max_coord,
) -> Pauli:
    return random_paulis(
        num=1,
        unique_qubits=False,
        int_coords=int_coords,
        tuple_coords=tuple_coords,
        dimension=dimension,
        max_dimension=max_dimension,
        from_letters=from_letters,
        from_signs=from_signs,
        min_coord=min_coord,
        max_coord=max_coord)[0]


def random_grouped_paulis(
        max_qubits: int,
        num_paulis: int,
        int_coords: bool = False,
        tuple_coords: bool = True,
        dimension: int = None,
        max_dimension: int = None,
        from_letters: List[str] = None,
        from_signs: List[complex] = None,
        min_coord: int | float = default_min_coord,
        max_coord: int | float = default_max_coord,
) -> Dict[Qubit, List[Pauli]]:
    unique_qubits = True
    qubits = random_qubits(
        max_qubits,
        unique_qubits,
        int_coords,
        tuple_coords,
        dimension,
        max_dimension,
        min_coord,
        max_coord)
    letters = random_pauli_letters(
        num_paulis, from_letters, from_signs)
    qubit_indexes = random.choices(range(max_qubits), k=num_paulis)

    # Ignore any qubits that haven't been randomly picked in `qubit_indexes`
    grouped_paulis = {qubits[j]: [] for j in set(qubit_indexes)}
    for i, j in enumerate(qubit_indexes):
        qubit = qubits[j]
        letter = letters[i]
        grouped_paulis[qubit].append(Pauli(qubit, letter))

    return grouped_paulis

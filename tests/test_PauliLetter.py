import random

import pytest

from main.Colour import Red, Green, Blue, Grey
from main.building_blocks.pauli.PauliLetter import PauliLetter
from tests.utils.numbers import random_complex_number


valid_letters = ['I', 'X', 'Y', 'Z']
valid_signs = [1, 0+1j, -1, 0-1j]


class NotAPauliLetter:
    def __init__(self, letter: str, sign: complex):
        self.letter = letter
        self.sign = sign


def test_pauli_letter_fails_if_letter_invalid():
    wrong = ['Nope', 'Sorry', 'A', 'B', 'C']
    for string in wrong:
        with pytest.raises(ValueError):
            _ = PauliLetter(string)
    for valid in valid_letters:
        _ = PauliLetter(valid)


def test_pauli_letter_fails_if_sign_invalid():
    repeats = 10
    for _ in range(repeats):
        sign = random_complex_number()
        if sign not in valid_signs:
            with pytest.raises(ValueError):
                _ = PauliLetter('I', sign)
    for valid in valid_signs:
        _ = PauliLetter('I', valid)


def test_pauli_letter_colour():
    expected = {
        'I': Grey,
        'X': Red,
        'Y': Blue,
        'Z': Green}
    for letter, colour in expected.items():
        pauli_letter = PauliLetter(letter)
        assert pauli_letter.colour == colour


def test_pauli_letter_inequality_if_letter_or_sign_are_different():
    repeats = 100
    for _ in range(repeats):
        letter_1 = random.choice(valid_letters)
        letter_2 = random.choice(valid_letters)
        sign_1 = random.choice(valid_signs)
        sign_2 = random.choice(valid_signs)
        pauli_letter_1 = PauliLetter(letter_1, sign_1)
        pauli_letter_2 = PauliLetter(letter_2, sign_2)
        if letter_1 != letter_2 or sign_1 != sign_2:
            assert pauli_letter_1 != pauli_letter_2


def test_pauli_letter_inequality_if_one_is_not_a_pauli_letter():
    repeats = 10
    for _ in range(repeats):
        letter_1 = random.choice(valid_letters)
        letter_2 = random.choice(valid_letters)
        sign_1 = random.choice(valid_signs)
        sign_2 = random.choice(valid_signs)
        pauli_letter = PauliLetter(letter_1, sign_1)
        not_a_pauli_letter = NotAPauliLetter(letter_2, sign_2)
        assert pauli_letter != not_a_pauli_letter


def test_pauli_letter_equality_if_letter_and_sign_are_equal():
    for letter in valid_letters:
        for sign in valid_signs:
            pauli_letter_1 = PauliLetter(letter, sign)
            pauli_letter_2 = PauliLetter(letter, sign)
            assert pauli_letter_1 == pauli_letter_2


def test_pauli_letter_repr():
    for letter in valid_letters:
        for sign in valid_signs:
            pauli_letter = PauliLetter(letter, sign)
            expected = {
                'letter': letter,
                'sign': sign}
            assert str(pauli_letter) == str(expected)


def test_pauli_letter_compose():
    # Usually one way to test something works is to find a second way to
    # define/calculate it, then compare the two. Bit annoying here because
    # the original method just works via a lookup table. Any other way
    # to define the expected outcome is a bit odd and cumbersome.
    repeats = 100
    for _ in range(repeats):
        letter_1 = random.choice(valid_letters)
        letter_2 = random.choice(valid_letters)
        sign_1 = random.choice(valid_signs)
        sign_2 = random.choice(valid_signs)
        pauli_letter_1 = PauliLetter(letter_1, sign_1)
        pauli_letter_2 = PauliLetter(letter_2, sign_2)

        result = pauli_letter_1.compose(pauli_letter_2)

        if letter_1 == 'I':
            assert result == PauliLetter(letter_2, sign_1 * sign_2)
        elif letter_2 == 'I':
            assert result == PauliLetter(letter_1, sign_1 * sign_2)
        elif letter_1 == letter_2:
            assert result == PauliLetter('I', sign_1 * sign_2)
        else:
            j_sign_pairs = [('X', 'Y'), ('Y', 'Z'), ('Z', 'X')]
            minus_j_sign_pairs = [('Y', 'X'), ('Z', 'Y'), ('X', 'Z')]
            if (letter_1, letter_2) in j_sign_pairs:
                extra_sign = 1j
            else:
                assert (letter_1, letter_2) in minus_j_sign_pairs
                extra_sign = -1j
            expected_letter = [
                letter for letter in valid_letters
                if letter not in ['I', letter_1, letter_2]][0]
            expected = PauliLetter(expected_letter, sign_1 * sign_2 * extra_sign)
            assert result == expected




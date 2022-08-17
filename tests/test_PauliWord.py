import operator
import random
from functools import reduce

import pytest

from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.pauli.PauliWord import PauliWord
from tests.utils.numbers import random_complex_number, default_test_repeats_small, default_test_repeats_medium
from tests.utils.paulis import random_pauli_word, valid_letters, valid_signs


class NotAPauliWord:
    def __init__(self, word: str, sign: complex):
        self.word = word
        self.sign = sign


def test_pauli_word_fails_if_word_invalid():
    wrong = ['Nope', 'Sorry', 'ABC', 'UVW', 'XYZ!']
    for string in wrong:
        with pytest.raises(ValueError):
            _ = PauliWord(string)


def test_pauli_word_fails_if_sign_invalid():
    repeats = default_test_repeats_small
    for _ in range(repeats):
        sign = random_complex_number()
        if sign not in valid_signs:
            with pytest.raises(ValueError):
                _ = PauliWord('I', sign)


def test_pauli_word_from_letters():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        length = random.randint(1, 100)
        letters = random.choices(valid_letters, k=length)
        signs = random.choices(valid_signs, k=length)
        pauli_letters = [
            PauliLetter(letter, sign)
            for letter, sign in zip(letters, signs)]
        pauli_word = PauliWord.from_letters(pauli_letters)
        assert pauli_word.word == ''.join(letters)
        assert pauli_word.sign == reduce(operator.mul, signs, 1)


def test_pauli_word_inequality_if_letter_or_sign_are_different():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        length = random.randint(1, 100)
        pauli_word_1 = random_pauli_word(length)
        pauli_word_2 = random_pauli_word(length)
        expect_unequal = \
            pauli_word_1.word != pauli_word_2.word or \
            pauli_word_1.sign != pauli_word_2.sign
        if expect_unequal:
            assert pauli_word_1 != pauli_word_2


def test_pauli_letter_inequality_if_one_is_not_a_pauli_letter():
    repeats = default_test_repeats_small
    for _ in range(repeats):
        length = random.randint(1, 100)
        pauli_word = random_pauli_word(length)
        not_a_pauli_word = NotAPauliWord(pauli_word.word, pauli_word.sign)
        assert pauli_word != not_a_pauli_word


def test_pauli_letter_equality_if_letter_and_sign_are_equal():
    repeats = default_test_repeats_small
    for _ in range(repeats):
        length = random.randint(1, 100)
        pauli_word_1 = random_pauli_word(length)
        pauli_word_2 = PauliWord(pauli_word_1.word, pauli_word_1.sign)
        assert pauli_word_1 == pauli_word_2


def test_pauli_word_repr():
    repeats = default_test_repeats_medium
    for _ in range(repeats):
        length = random.randint(1, 100)
        pauli_word = random_pauli_word(length)
        expected = {
            'word': pauli_word.word,
            'sign': pauli_word.sign}
        assert str(pauli_word) == str(expected)

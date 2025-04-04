import random
import string

from main.utils.utils import xor


def random_strings(
        num: int,
        length: int = None,
        max_length: int = None,
        uppercase: bool = False,
        lowercase: bool = False,
        allow_numbers: bool = True,
        punctuation: str = None,
        allow_spaces: bool = False
):
    validate_arguments(
        length,
        max_length,
        uppercase,
        lowercase)

    # Define the desired character set
    characters = ''
    # First define permitted letters
    if uppercase:
        characters += string.ascii_uppercase
    elif lowercase:
        characters += string.ascii_lowercase
    else:
        characters += string.ascii_letters
    # Then numbers
    if allow_numbers:
        characters += string.digits
    # Then special characters
    if punctuation is None:
        punctuation = ''
    characters += punctuation
    if allow_spaces:
        punctuation += ' '

    # Define the lengths of each of the `num` strings
    lengths = [length for _ in range(num)] \
        if length is not None \
        else random.choices(range(1, max_length + 1), k=num)
    total_length = sum(lengths)

    # Now create one big string...
    total_string = ''.join(random.choices(characters, k=total_length))
    # ... then chunk it up into `num` smaller strings
    strings = []
    processed = 0
    for length in lengths:
        next_processed = processed + length
        strings.append(total_string[processed: next_processed])
        processed = next_processed

    return strings


def random_string(
        length: int,
        uppercase: bool = False,
        lowercase: bool = False,
        allow_numbers: bool = True,
        punctuation: str = None,
        allow_spaces: bool = False
):
    return random_strings(
        num=1,
        length=length,
        uppercase=uppercase,
        lowercase=lowercase,
        allow_numbers=allow_numbers,
        punctuation=punctuation,
        allow_spaces=allow_spaces)[0]


def validate_arguments(
        length: int = None,
        max_length: int = None,
        uppercase: bool = False,
        lowercase: bool = False):
    assert xor(length is not None, max_length is not None)
    assert not (uppercase and lowercase)

from __future__ import annotations
from main.Colour import Red, Blue, Green, Grey
from main.utils.NiceRepr import NiceRepr


# TODO - use stim.PauliString stuff instead? Has many operations built-in.
#  Could then maybe do away with all instances of using PauliX (say) as a
#  key in a dictionary, and just replace it with the equivalent Stim object?
#  (For 'could', maybe read 'should'?)
class PauliLetter(NiceRepr):
    def __init__(self, letter: str, sign: complex = 1):
        if letter not in ['I', 'X', 'Y', 'Z']:
            raise ValueError(
                f"Only valid Pauli letters are I, X, Y and Z. "
                f"Cannot use {letter} as a PauliLetter")
        if sign not in [1, 0+1j, -1, 0-1j]:
            raise ValueError(
                f"Only valid signs are 1, j, -1, -j. "
                f"Cannot use {sign} as a sign for a PauliLetter.")
        self.letter = letter
        self.sign = sign

        # Paulis come with a default colour to be used e.g. when printing.
        # Not to be confused with the colour of an edge/plaquette/etc. when
        # using (for example) the colour code.
        self.colour = pauli_colours[letter]
        super().__init__(['letter', 'sign'])

    def compose(self, other: PauliLetter):
        sign, letter = multiplication_table[(self.letter, other.letter)]
        sign *= self.sign * other.sign
        return PauliLetter(letter, sign)

    def __eq__(self, other):
        return \
            type(other) == type(self) and \
            self.letter == other.letter and \
            self.sign == other.sign

    def __hash__(self):
        return hash((self.letter, self.sign))


# Would like to have put this in the pauli/utils.py file, but circular
# references make this too annoying.
multiplication_table = {
    ('I', 'I'): (1, 'I'),
    ('I', 'X'): (1, 'X'),
    ('I', 'Y'): (1, 'Y'),
    ('I', 'Z'): (1, 'Z'),
    ('X', 'I'): (1, 'X'),
    ('X', 'X'): (1, 'I'),
    ('X', 'Y'): (1j, 'Z'),
    ('X', 'Z'): (-1j, 'Y'),
    ('Y', 'I'): (1, 'Y'),
    ('Y', 'X'): (-1j, 'Z'),
    ('Y', 'Y'): (1, 'I'),
    ('Y', 'Z'): (1j, 'X'),
    ('Z', 'I'): (1, 'Z'),
    ('Z', 'X'): (1j, 'Y'),
    ('Z', 'Y'): (-1j, 'X'),
    ('Z', 'Z'): (1, 'I')}


pauli_colours = {
    'X': Red,
    'Y': Blue,
    'Z': Green,
    'I': Grey}


# TODO - these are going to lead to obscure bugs!!!
#   These mean the same object is being reused multiple times all over
#   the place. Should instead create a new object every time.
PauliI = PauliLetter('I')
PauliX = PauliLetter('X')
PauliY = PauliLetter('Y')
PauliZ = PauliLetter('Z')

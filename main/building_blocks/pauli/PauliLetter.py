from __future__ import annotations
from main.Colour import Colour, Red, Blue, Green, Black
from main.utils.DebugFriendly import DebugFriendly


# TODO - use stim.PauliString stuff instead? Has many operations built-in.
#  Could then maybe do away with all instances of using PauliX (say) as a
#  key in a dictionary? (For 'could', maybe read 'should'?)
class PauliLetter(DebugFriendly):
    def __init__(self, letter: str, sign: complex = 1):
        self.letter = letter
        self.sign = sign
        # Paulis come with a default colour to be used e.g. when printing.
        # Not to be confused with the colour of an edge/plaquette/etc. when
        # using e.g. colour code.
        colours = {
            'X': Red,
            'Y': Blue,
            'Z': Green,
            'I': Black}
        self.colour = colours[letter]
        self.multiplication_table = {
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
            ('Z', 'Z'): (1, 'I'),
        }
        super().__init__(['letter', 'sign'])

    def compose(self, other: PauliLetter):
        sign, letter = self.multiplication_table[(self.letter, other.letter)]
        sign *= self.sign * other.sign
        return PauliLetter(letter, sign)

    def __eq__(self, other):
        return \
            type(other) == type(self) and \
            self.letter == other.letter and \
            self.sign == other.sign

    def __hash__(self):
        return hash((self.letter, self.sign))


PauliI = PauliLetter('I')
PauliX = PauliLetter('X')
PauliY = PauliLetter('Y')
PauliZ = PauliLetter('Z')
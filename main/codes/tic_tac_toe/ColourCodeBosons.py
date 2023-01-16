from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.utils.Colour import Red, Green, Blue

class ColourCodeBoson(dict):
    def __init__(self, colour, pauli_letter: PauliLetter):
        self.colour=colour
        self.pauli_letter=pauli_letter

    def __mul__(self, other):
        """Fuses two colour code anyons. 

        Returns:
            Resulting colour code anyon from fusion.
        """
        if self.colour != other.colour and self.pauli_letter.letter != other.pauli_letter.letter:
            raise 'These two bosons don\'t fuse to a fermion'

        elif self.colour == other.colour and self.pauli_letter.letter != other.pauli_letter.letter:
            colour = self.colour
            pauli_letter =  PauliLetter(({'X','Y','Z'} - set((self.pauli_letter.letter, other.pauli_letter.letter))).pop())
        elif self.colour != other.colour and self.pauli_letter.letter == other.pauli_letter.letter:
            pauli_letter = self.pauli_letter
            colour = {Red, Green, Blue} - set((self.colour, other.colour))
        else:
            return(ColourCodeBoson(self.colour, self.pauli_letter))
        return(ColourCodeBoson(colour, pauli_letter))

    def __repr__(self) -> str:
        return(str(self.colour.name[0])+str(self.pauli_letter.letter))

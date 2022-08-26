from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.Qubit import Qubit
from main.utils.NiceRepr import NiceRepr


# When we use stim.Paulistring instead of PauliLetter, this will become a wrapper of
# stim.PauliStringer
class Pauli(NiceRepr):
    """Class for represting a single Pauli operator on a specific qubit

    Attributes
        qubit: Qubit on which the Pauli operator acts
        letter: The PauliLetter contains the phase and letter.
        dimension: The dimension in which the qubit is embedded, i.e. the number of
                         coordinates used to specify the position of the qubit.
    """

    def __init__(self, qubit: Qubit, letter: PauliLetter):
        """Inits Pauli

        Args:
            qubit: Qubit on which the Pauli operator acts
            letter: The PauliLetter contains the phase and letter.
        """
        self.qubit = qubit
        self.letter = letter
        self.dimension = qubit.dimension
        super().__init__(["qubit", "letter"])

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self.qubit == other.qubit
            and self.letter == other.letter
        )

    def __hash__(self):
        return hash((self.qubit, self.letter))

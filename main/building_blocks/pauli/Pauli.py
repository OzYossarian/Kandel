from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.Qubit import Qubit
from main.utils.NiceRepr import NiceRepr


# When we use stim.Paulistring instead of PauliLetter, one of the inputs to the constructor will be stim.Paulistring
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
        super().__init__(["qubit", "letter"])

    @property
    def dimension(self):
        return self.qubit.dimension

    @property
    def has_tuple_coords(self):
        return self.qubit.has_tuple_coords

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self.qubit == other.qubit
            and self.letter == other.letter
        )

    def __hash__(self):
        return hash((self.qubit, self.letter))

from main.building_blocks.Pauli import Pauli
from main.building_blocks.Qubit import Qubit
from main.utils import DebugFriendly


class Operator(DebugFriendly):
    def __init__(self, qubit: Qubit, pauli: Pauli):
        self.qubit = qubit
        self.pauli = pauli
        super().__init__(['qubit', 'pauli'])

    def __eq__(self, other):
        if isinstance(other, Operator) \
                and self.qubit == other.qubit \
                and self.pauli == other.pauli:
            return True
        else:
            return False

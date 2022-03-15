from main.building_blocks.Pauli import Pauli
from main.building_blocks.Qubit import Qubit


class Operator:
    def __init__(self, qubit: Qubit, pauli: Pauli):
        self.qubit = qubit
        self.pauli = pauli

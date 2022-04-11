from main.building_blocks.Pauli import Pauli
from main.building_blocks.Qubit import Qubit


class Operator(object):
    def __init__(self, qubit: Qubit, pauli: Pauli):
        self.qubit = qubit
        self.pauli = pauli

    def __repr__(self):
        return f"Operator acting on qubits \n   {self.qubit} \nWith pauli \n    pauli={self.pauli}\n"

    def __eq__(self, other):
        if isinstance(other, Operator) \
                and self.qubit == other.qubit \
                and self.pauli == other.pauli:
            return True
        else:
            return False

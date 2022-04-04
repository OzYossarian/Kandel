from typing import List

from main.Colour import Colour
from main.building_blocks.Operator import Operator
from main.building_blocks.Pauli import Pauli
from main.building_blocks.Qubit import Qubit, Coordinates


class Check:
    def __init__(self, operators: List[Operator], center: Coordinates = None,
                 ancilla: Qubit = None, colour: Colour = None,
                 pauli_type: Pauli = None, initialization_timestep: int = None):
        """
        TODO write description here
        """
        self.operators = operators
        self.ancilla = ancilla
        self.center = center
        self.colour = colour
        self.pauli_type = pauli_type

    def __repr__(self):
        return(f"""Check using ancilla operator \n     {self.ancilla}
               \nwith operators \n   {self.operators}\n""")

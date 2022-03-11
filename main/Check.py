from typing import Dict
from main.Qubit import Qubit, Coordinates
from main.enums import Pauli, Colour


class Check:
    def __init__(self, operators: Dict[Qubit, Pauli], ancilla: Qubit,
                 center: Coordinates, colour: Colour,
                 pauli_type: Pauli | None):
        self.operators = operators
        self.ancilla = ancilla
        self.center = center
        self.colour = colour
        self.pauli_type = pauli_type


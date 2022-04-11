from typing import List

from main.Colour import Colour
from main.building_blocks.Operator import Operator
from main.building_blocks.Qubit import Qubit, Coordinates


class Check:
    def __init__(self, operators: List[Operator], center: Coordinates = None,
                 ancilla: Qubit = None, colour: Colour = None,
                 initialization_timestep: int = 0):
        self.operators = operators
        self.center = center
        self.colour = colour
        self.ancilla = ancilla
        self.initialization_timestep = initialization_timestep

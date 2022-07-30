from typing import Dict

from main.building_blocks.Qubit import Qubit
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.enums import State


class LogicalQubit:
    def __init__(
            self, x: LogicalOperator, z: LogicalOperator):
        self.x = x
        self.z = z

from typing import List
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.pauli.Pauli import Pauli


class StabilityOperator(LogicalOperator):
    def __init__(self, rounds_to_use: List, code):
        self.rounds_to_use = rounds_to_use
        self._at_round = {-1: None}
        self.code = code

        super().__init__([])

    def at_round(self, round: int):
        if round in self.rounds_to_use:
            return self.update(round)
        else:
            return ([])

    def update(self, round: int):
        if round in self.rounds_to_use:
            checks = self.code.check_schedule[round %
                                              self.code.schedule_length]
        else:
            checks = []

        return checks

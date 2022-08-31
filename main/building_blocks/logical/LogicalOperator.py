import warnings

from typing import List

from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.utils import compose


class LogicalOperator:
    def __init__(self, paulis: List[Pauli]):
        # The logical operator may move around, so we'll store its values
        # at the end of different rounds.
        self._at_round = {-1: paulis}
        self.last_activity = -1

    def update(self, round: int, other_paulis: List[Pauli]):
        if round <= self.last_activity:
            # TODO - should this be a warning?
            warnings.warn(
                f'Operator has already been updated for this round! Asked '
                f'to update for round {round}, but was already updated for '
                f'round {self.last_activity}')
        else:
            # Compose the logical operator with these new paulis, to give
            # a new logical operator. Order matters!
            paulis = compose(
                other_paulis + self.at_round(round - 1),
                identities_removed=True)
            self._at_round[round] = paulis
            self.last_activity = round

    def at_round(self, round: int):
        if round > self.last_activity:
            # If there's nothing stored yet for this round, assume nothing
            # has changed, so operator is the same as last time it was stored.
            for r in range(self.last_activity + 1, round + 1):
                self._at_round[r] = self._at_round[self.last_activity]
            self.last_activity = round
        return self._at_round[round]


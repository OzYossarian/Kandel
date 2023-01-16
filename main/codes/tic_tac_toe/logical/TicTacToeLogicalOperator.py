from __future__ import annotations

from typing import List, TYPE_CHECKING

from main.building_blocks.Check import Check
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.pauli.utils import compose
if TYPE_CHECKING:
    from main.codes.tic_tac_toe.logical.TicTacToeLogicalQubit import TicTacToeLogicalQubit


class TicTacToeLogicalOperator(LogicalOperator):
    def __init__(
            self,
            initial_paulis: List[Pauli],
            is_vertical: bool,
            logical_letter: PauliLetter,
            logical_qubit: TicTacToeLogicalQubit):
        """
        A logical operator specifically for a TicTacToeCode. Here the
        logical operator may move around without repeating, so we won't
        generate its constituent Paulis at every round upfront. Instead,
        we'll build a dict of its values at different rounds as we go.

        Args:
            initial_paulis:
                the Paulis that make up the operator before any checks have
                been measured ("at round -1")
            is_vertical:
                whether this operator runs vertically across our square
                tic-tac-toe code or not.
            logical_letter:
                which operator this represents - either PauliLetter('X') or PauliLetter('Z')
            logical_qubit:
                the logical qubit this operator is part of.
        """
        assert logical_letter in [PauliLetter('X'), PauliLetter('Z')]

        self._at_round = {-1: initial_paulis}
        self.last_updated = -1
        self.logical_letter = logical_letter
        self.is_vertical = is_vertical
        self.logical_qubit = logical_qubit
        super().__init__([])

    def at_round(self, round: int):
        if round not in self._at_round:
            # If there's nothing stored yet for this round, figure out what
            # the logical at this point should be.
            # need to do something with a loop?
            if round-1 not in self._at_round:
                raise ValueError(
                    'The logical operator has not yet been compiled in the previous round.'
                )

            for r in range(self.last_updated + 1, round + 1):
                self.update(r)
        return self._at_round[round]

    def update(self, just_measured_round: int):
        """Updates the logical operator.

        Args:
            just_measured_round: The index of the round that has just been measured.

        Returns:
            checks_multiplied_in: Checks with which the logical operator has been multiplied.
        """
        prev_x_boson = self.logical_qubit.x_boson
        prev_z_boson = self.logical_qubit.z_boson

        next_x_boson, next_z_boson = self.logical_qubit.get_next_bosons(just_measured_round)
        if self.logical_letter == PauliLetter('X'):
            next_boson, prev_boson = next_x_boson, prev_x_boson
        else:
            next_boson, prev_boson = next_z_boson, prev_z_boson

        if next_boson != prev_boson:
            checks_multiplied_in = self.multiply_by_checks(just_measured_round)
        else:
            # Nothing to be done! All stays the same.
            self._at_round[just_measured_round] = self.at_round(just_measured_round-1)
            checks_multiplied_in = []
            self.last_updated += 1
        return checks_multiplied_in

    def multiply_by_checks(self, round: int):
        relative_round = round % self.logical_qubit.code.schedule_length
        check_type = self.logical_qubit.code.tic_tac_toe_route[relative_round]
        checks = self.logical_qubit.code.checks_by_type[check_type]
        intersecting_checks = [
            check for check in checks
            if self.intersects(check, round)]
        # Slightly different depending on whether operator is vertical or
        # horizontal - horizontal operators are multiplied by ALL
        # intersecting checks, whereas vertical ones are only multiplied by
        # those in their support (i.e. not horizontal ones).
        if self.is_vertical:
            intersecting_checks = [
                check for check in intersecting_checks
                if not self.is_horizontal(check)]
        intersecting_paulis = [
            pauli
            for check in intersecting_checks
            for pauli in check.paulis.values()]

        new_paulis = compose(
            intersecting_paulis + self.at_round(round - 1),
            identities_removed=True)
        self._at_round[round] = new_paulis
        self.last_updated = round

        return intersecting_checks

    def intersects(self, check: Check, round: int):
        # It's possible for the Paulis that make up the operator to
        # contain an identity Pauli with some sign - only consider checks
        # that touch the operator at a non-identity Pauli to be
        # intersecting.
        check_qubits = {pauli.qubit for pauli in check.paulis.values()}
        return any(
            pauli.letter.letter != 'I' and pauli.qubit in check_qubits
            for pauli in self.at_round(round - 1))

    @staticmethod
    def is_horizontal(check: Check):
        y_coords = [pauli.qubit.coords[1] for pauli in check.paulis.values()]
        return len(set(y_coords)) == 1

from __future__ import annotations

from typing import TYPE_CHECKING

from main.utils.Colour import Red, Blue, Green
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter

if TYPE_CHECKING:
    from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.codes.tic_tac_toe.logical.TicTacToeLogicalOperator import (
    TicTacToeLogicalOperator,
)
from main.codes.tic_tac_toe.utils import rest_of_row, rest_of_column, TicTacToeSquare


class TicTacToeLogicalQubit(LogicalQubit):
    def __init__(
        self,
        vertical_pauli_letter: PauliLetter,
        horizontal_pauli_letter: PauliLetter,
        code: TicTacToeCode,
    ):
        """Class for the dynamical logical operators of TicTacToe codes.

        Args:
            vertical_pauli_letter: The pauli letter we label the vertical observable with.
            horizontal_pauli_letter: The pauli letter we label the horizontal observable with.
            code: Instance of TicTacToeCode
        """
        self.code = code
        self.vertical = vertical_pauli_letter
        self.horizontal = horizontal_pauli_letter
        assert {self.vertical, self.horizontal} == {PauliLetter("X"), PauliLetter("Z")}

        self.vertical_operator_starts = {Red: (6, 4), Blue: (6, 0), Green: (6, 8)}
        self.horizontal_operator_starts = {Red: (8, 2), Blue: (2, 4), Green: (8, 6)}
        (
            self.X_equivalent_bosons,
            self.Z_equivalent_bosons,
            self.x_boson,
            self.z_boson,
        ) = self.get_initial_X_and_Z_boson(code.gauge_factor)

        if self.vertical == PauliLetter("X"):
            x_operator = self.get_initial_vertical_operator(
                PauliLetter("X"), self.x_boson
            )
            z_operator = self.get_initial_horizontal_operator(
                PauliLetter("Z"), self.z_boson
            )
        else:
            z_operator = self.get_initial_vertical_operator(
                PauliLetter("Z"), self.z_boson
            )
            x_operator = self.get_initial_horizontal_operator(
                PauliLetter("X"), self.x_boson
            )

        super().__init__(x=x_operator, z=z_operator)

    def get_initial_X_and_Z_boson(self, gauge_factor=1):
        """Returns the initial colour and pauli letter of the boson of the X and Z logical.

        Returns:
            X_equivalent_bosons: Two bosons which are equivalent of which one is X_boson_init.
            Z_equivalent_bosons: Two bosons which are equivalent of which one is Z_boson_init.
            X_boson_init: Colour and pauli letter of logical X boson.
            Z_boson_init: Colour and pauli letter of logical Z boson.
        """
        boson_colour, boson_letter = self.code.tic_tac_toe_route[0]

        # In gauge tictactoe codes the same boson can be condonsed in the first two rounds.
        (next_colour, next_letter) = self.code.tic_tac_toe_route[gauge_factor]


        next_row = rest_of_row(next_colour, next_letter)
        next_column = rest_of_column(next_colour, next_letter)

        if boson_letter.letter == "X" or boson_letter.letter == "Y":
            X_equivalent_bosons = rest_of_row(boson_colour, boson_letter)
            X_boson_init = set(X_equivalent_bosons).intersection(next_column).pop()

            Z_equivalent_bosons = rest_of_column(boson_colour, boson_letter)
            Z_boson_init = set(Z_equivalent_bosons).intersection(next_row).pop()

        elif boson_letter.letter == "Z":
            X_equivalent_bosons = rest_of_column(boson_colour, boson_letter)
            X_boson_init = set(X_equivalent_bosons).intersection(next_row).pop()

            Z_equivalent_bosons = rest_of_row(boson_colour, boson_letter)
            Z_boson_init = set(Z_equivalent_bosons).intersection(next_column).pop()

        return (X_equivalent_bosons, Z_equivalent_bosons, X_boson_init, Z_boson_init)

    def get_next_bosons(self, just_measured_round: int):
        """Returns the next bosons of the logical operators.

        Args:
            just_measured_round: The index of the round that we've just finished doing measurements for.

        Returns:
            X_intersection: X logical boson. This is the boson that is in the X equivalent bosons in just_measured_round
                            and just_measured_round+1
            Z_intersection: Z logical boson. This is the boson that is in the Z equivalent bosons in just_measured_round
                            and just_measured_round+1
        """

        # The bosons returned will be the bosons of the operators immediately
        # after round 'round' up until right before round 'round + 1'.

        next_round = (just_measured_round + 1) % len(self.code.tic_tac_toe_route)

        if (
            self.code.tic_tac_toe_route[
                just_measured_round % len(self.code.tic_tac_toe_route)
            ]
            == self.code.tic_tac_toe_route[next_round]
        ):
            return (self.x_boson, self.z_boson)

        (next_colour, next_letter) = self.code.tic_tac_toe_route[next_round]
        next_row = rest_of_row(next_colour, next_letter)
        next_column = rest_of_column(next_colour, next_letter)

        # figure out which are the X bosons and Z bosons
        X_intersection = set(self.X_equivalent_bosons).intersection(next_column)
        if X_intersection == set():
            X_intersection = set(self.X_equivalent_bosons).intersection(next_row).pop()
            Z_intersection = (
                set(self.Z_equivalent_bosons).intersection(next_column).pop()
            )
            self.X_equivalent_bosons = next_row
            self.Z_equivalent_bosons = next_column

        else:
            X_intersection = X_intersection.pop()
            Z_intersection = set(self.Z_equivalent_bosons).intersection(next_row).pop()
            self.X_equivalent_bosons = next_column
            self.Z_equivalent_bosons = next_row
        self.x_boson = X_intersection
        self.z_boson = Z_intersection
        return X_intersection, Z_intersection

    def get_initial_vertical_operator(
        self, logical_pauli_letter: PauliLetter, tic_tac_toe_square: TicTacToeSquare
    ):
        """Initializes one of the two vertical logical operators.

        Args:
            logical_pauli_letter: The label of this operator.
            tic_tac_toe_square: The boson colour and boson pauli letter of the logical operator.

        Returns:
            A TicTacToeLogicalOperator
        """
        colour, letter = tic_tac_toe_square
        start = self.vertical_operator_starts[colour]
        paulis = []
        for i in range(self.code.distance // 2):
            u = (start[0] + (i % 2) * 2, start[1] + 6 * i)
            v = (start[0] + 2 - (i % 2) * 2, start[1] + 2 + 6 * i)
            qubit_u = self.code.data_qubits[self.code.wrap_coords(u)]
            qubit_v = self.code.data_qubits[self.code.wrap_coords(v)]
            pauli_u = Pauli(qubit_u, letter)
            pauli_v = Pauli(qubit_v, letter)
            paulis.extend([pauli_u, pauli_v])
        is_vertical = True

        return TicTacToeLogicalOperator(
            paulis, is_vertical, logical_pauli_letter, logical_qubit=self
        )

    def get_initial_horizontal_operator(
        self, logical_pauli_letter: PauliLetter, tic_tac_toe_square: TicTacToeSquare
    ):
        """Initializes one of the two horizontal logical operators.

        Args:
            logical_pauli_letter: The label of this operator.
            tic_tac_toe_square: The boson colour and boson pauli letter of the logical operator.

        Returns:
            A TicTacToeLogicalOperator
        """
        colour, _ = tic_tac_toe_square
        start = self.horizontal_operator_starts[colour]
        paulis = []
        for i in range(self.code.distance // 2):
            u = (start[0] + 12 * i, start[1])
            v = (u[0] + 4, u[1])
            qubit_u = self.code.data_qubits[self.code.wrap_coords(u)]
            qubit_v = self.code.data_qubits[self.code.wrap_coords(v)]
            pauli_u = Pauli(qubit_u, logical_pauli_letter)
            pauli_v = Pauli(qubit_v, logical_pauli_letter)
            paulis.extend([pauli_u, pauli_v])
        is_vertical = False
        return TicTacToeLogicalOperator(
            paulis, is_vertical, logical_pauli_letter, logical_qubit=self
        )

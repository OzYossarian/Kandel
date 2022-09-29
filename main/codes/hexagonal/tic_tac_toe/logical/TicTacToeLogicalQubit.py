from __future__ import annotations

from typing import TYPE_CHECKING

from main.utils.Colour import Red, Blue, Green
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter, PauliX, PauliZ
if TYPE_CHECKING:
    from main.codes.hexagonal.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.codes.hexagonal.tic_tac_toe.logical.TicTacToeLogicalOperator import TicTacToeLogicalOperator
from main.codes.hexagonal.tic_tac_toe.utils import rest_of_row, rest_of_column, TicTacToeSquare


class TicTacToeLogicalQubit(LogicalQubit):
    def __init__(
            self,
            vertical: PauliLetter,
            horizontal: PauliLetter,
            code: TicTacToeCode):
        self.code = code
        self.vertical = vertical
        self.horizontal = horizontal
        assert {self.vertical, self.horizontal} == {PauliX, PauliZ}

        self.vertical_operator_starts = {
            Red: (6, 4),
            Blue: (6, 0),
            Green: (6, 8)}
        self.horizontal_operator_starts = {
            Red: (8, 2),
            Blue: (2, 4),
            Green: (8, 6)}

        initial_x_type, initial_z_type = self.get_types(round=-1)
        if vertical == PauliX:
            x_operator = self.get_initial_vertical_operator(
                PauliX, initial_x_type)
            z_operator = self.get_initial_horizontal_operator(
                PauliZ, initial_z_type)
        else:
            x_operator = self.get_initial_horizontal_operator(
                PauliX, initial_x_type)
            z_operator = self.get_initial_vertical_operator(
                PauliZ, initial_z_type)

        super().__init__(x=x_operator, z=z_operator)

    def get_types(self, round: int):
        # 'round' is the round we've just finished doing measurements for.
        # The types returned will be the types of the operators immediately
        # after round 'round' up until right before round 'round + 1'.
        relative_round = round % len(self.code.tic_tac_toe_route)
        (prev_colour, prev_letter) = self.code.tic_tac_toe_route[relative_round]
        prev_row = rest_of_row(prev_colour, prev_letter)
        prev_column = rest_of_column(prev_colour, prev_letter)

        next_round = (relative_round + 1) % len(self.code.tic_tac_toe_route)
        (next_colour, next_letter) = self.code.tic_tac_toe_route[next_round]
        next_row = rest_of_row(next_colour, next_letter)
        next_column = rest_of_column(next_colour, next_letter)

        row_column_intersection = \
            set(prev_row).intersection(next_column).pop()
        column_row_intersection = \
            set(prev_column).intersection(next_row).pop()

        if round % 2 == 0:
            x_type = row_column_intersection
            z_type = column_row_intersection
        else:
            x_type = column_row_intersection
            z_type = row_column_intersection

        return x_type, z_type

    def get_initial_horizontal_operator(
            self,
            logical_letter: PauliLetter,
            tic_tac_toe_square: TicTacToeSquare):
        colour, letter = tic_tac_toe_square
        start = self.horizontal_operator_starts[colour]
        paulis = []
        for i in range(self.code.distance // 2):
            u = (start[0] + 12*i, start[1])
            v = (u[0] + 4, u[1])
            qubit_u = self.code.data_qubits[self.code.wrap_coords(u)]
            qubit_v = self.code.data_qubits[self.code.wrap_coords(v)]
            pauli_u = Pauli(qubit_u, letter)
            pauli_v = Pauli(qubit_v, letter)
            paulis.extend([pauli_u, pauli_v])
        is_vertical = False
        return TicTacToeLogicalOperator(
            paulis, is_vertical, logical_letter, logical_qubit=self)

    def get_initial_vertical_operator(
            self,
            logical_letter: PauliLetter,
            tic_tac_toe_square: TicTacToeSquare):
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
            paulis, is_vertical, logical_letter, logical_qubit=self)

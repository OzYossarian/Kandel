from __future__ import annotations

from typing import TYPE_CHECKING

from main.utils.Colour import Red, Blue, Green
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
if TYPE_CHECKING:
    from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.codes.tic_tac_toe.logical.TicTacToeLogicalOperator import TicTacToeLogicalOperator
from main.codes.tic_tac_toe.utils import rest_of_row, rest_of_column, TicTacToeSquare


class TicTacToeLogicalQubit(LogicalQubit):
    def __init__(
            self,
            vertical: PauliLetter,
            horizontal: PauliLetter,
            even_rows: PauliLetter,
            odd_rows: PauliLetter,
            code: TicTacToeCode,
    ):
        """Class for the dynamical logical operators of TicTacToe codes.

        Args:
            vertical:
                The Pauli letter (X or Z) we label the vertical observable with.
            horizontal:
                The Pauli letter (X or Z) we label the horizontal observable with.
            even_rows:
                At any timestep t, suppose we've just measured edges with
                colour c and Pauli type p. Consider the tic-tac-toe square
                (c, p). The row containing this square describes the types of
                edges that support one logical operator (X or Z) immediately
                after timestep t, while the column containing this square
                describes the types of edges supporting the other operator.

                At every timestep, this alternates: if the support of logical
                X (say) was described by the row containing (c, p) immediately
                after time t, then it's described by the column containing
                (c', p') immediately after time t+1, where c' and p' are the
                colour and Pauli type of the edges measured at time t+1.

                This parameter `even_rows` thus tells us which logical
                operator (X or Z) has support described by rows of the
                tic-tac-toe grid immediately after even timesteps (and hence
                by columns of the grid immediately after odd timesteps).
            odd_rows:
                As above, but for odd rather than even timesteps.
            code: TicTacToeCode that this qubit is part of
        """
        self.code = code
        self.vertical = vertical
        self.horizontal = horizontal
        self.even_rows = even_rows
        self.odd_rows = odd_rows

        x_and_z = {PauliLetter("X"), PauliLetter("Z")}
        assert {self.vertical, self.horizontal} == x_and_z
        assert {self.even_rows, self.odd_rows} == x_and_z

        self.vertical_operator_starts = {
            Red: (6, 4),
            Blue: (6, 0),
            Green: (6, 8)}
        self.horizontal_operator_starts = {
            Red: (8, 2),
            Blue: (2, 4),
            Green: (8, 6)}

        initial_x_type, initial_z_type = self.get_types(round=-1)
        if vertical == PauliLetter('X'):
            x_operator = self.get_initial_vertical_operator(
                PauliLetter('X'), initial_x_type)
            z_operator = self.get_initial_horizontal_operator(
                PauliLetter('Z'), initial_z_type)
        else:
            x_operator = self.get_initial_horizontal_operator(
                PauliLetter('X'), initial_x_type)
            z_operator = self.get_initial_vertical_operator(
                PauliLetter('Z'), initial_z_type)

        super().__init__(x=x_operator, z=z_operator)

    def get_types(self, round: int):
        # 'round' is the round we've just finished doing measurements for.
        # The types returned will be the types of the operators immediately
        # after round 'round' up until right before round 'round + 1'.
        relative_round = round % len(self.code.tic_tac_toe_route)
        (prev_colour,
         prev_letter) = self.code.tic_tac_toe_route[relative_round]
        prev_row = rest_of_row(prev_colour, prev_letter)
        prev_column = rest_of_column(prev_colour, prev_letter)

        next_round = (relative_round + 1) % len(self.code.tic_tac_toe_route)
        (next_colour, next_letter) = self.code.tic_tac_toe_route[next_round]
        next_row = rest_of_row(next_colour, next_letter)
        next_column = rest_of_column(next_colour, next_letter)

        prev_row_next_column_intersection = \
            set(prev_row).intersection(next_column).pop()
        prev_column_next_row_intersection = \
            set(prev_column).intersection(next_row).pop()

        row_describes_x_support = \
            round % 2 == 0 and self.even_rows == PauliLetter('X') or \
            round % 2 == 1 and self.odd_rows == PauliLetter('X')
        if row_describes_x_support:
            x_type = prev_row_next_column_intersection
            z_type = prev_column_next_row_intersection
        else:
            x_type = prev_column_next_row_intersection
            z_type = prev_row_next_column_intersection

        return x_type, z_type

    def get_initial_horizontal_operator(
            self,
            logical_pauli_letter: PauliLetter,
            tic_tac_toe_square: TicTacToeSquare):
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
        for i in range(self.code.columns // 2):
            u = (start[0] + 12 * i, start[1])
            v = (u[0] + 4, u[1])
            qubit_u = self.code.data_qubits[self.code.wrap_coords(u)]
            qubit_v = self.code.data_qubits[self.code.wrap_coords(v)]
            pauli_u = Pauli(qubit_u, logical_pauli_letter)
            pauli_v = Pauli(qubit_v, logical_pauli_letter)
            paulis.extend([pauli_u, pauli_v])
        is_vertical = False
        return TicTacToeLogicalOperator(
            paulis, is_vertical, logical_pauli_letter, logical_qubit=self)

    def get_initial_vertical_operator(
            self,
            logical_pauli_letter: PauliLetter,
            tic_tac_toe_square: TicTacToeSquare):
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
        for i in range(int((4/3*self.code.rows) // 2)):
            u = (start[0] + (i % 2) * 2, start[1] + 6 * i)
            v = (start[0] + 2 - (i % 2) * 2, start[1] + 2 + 6 * i)
            qubit_u = self.code.data_qubits[self.code.wrap_coords(u)]
            qubit_v = self.code.data_qubits[self.code.wrap_coords(v)]
            pauli_u = Pauli(qubit_u, letter)
            pauli_v = Pauli(qubit_v, letter)
            paulis.extend([pauli_u, pauli_v])
        is_vertical = True
        return TicTacToeLogicalOperator(
            paulis, is_vertical, logical_pauli_letter, logical_qubit=self)

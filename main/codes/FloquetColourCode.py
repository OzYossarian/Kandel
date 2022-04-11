from main.Colour import Red, Green, Blue
from main.building_blocks.Pauli import PauliX, PauliZ
from main.codes.TicTacToeCode import TicTacToeCode


class FloquetColourCode(TicTacToeCode):
    def __init__(self, distance: int):
        tic_tac_toe = [
            (Red, PauliX),
            (Green, PauliZ),
            (Blue, PauliX),
            (Red, PauliZ),
            (Green, PauliX),
            (Blue, PauliZ),
        ]
        super().__init__(distance, tic_tac_toe)

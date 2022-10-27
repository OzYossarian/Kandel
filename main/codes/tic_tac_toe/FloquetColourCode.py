from main.utils.Colour import Red, Green, Blue
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode


class FloquetColourCode(TicTacToeCode):
    def __init__(self, distance: int):
        tic_tac_toe = [
            (Red, PauliLetter('X')),
            (Green, PauliLetter('Z')),
            (Blue, PauliLetter('X')),
            (Red, PauliLetter('Z')),
            (Green, PauliLetter('X')),
            (Blue, PauliLetter('Z')),
        ]
        super().__init__(distance, tic_tac_toe)

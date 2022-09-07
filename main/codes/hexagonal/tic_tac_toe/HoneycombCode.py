from main.utils.Colour import Red, Green, Blue
from main.building_blocks.pauli.PauliLetter import PauliX, PauliY, PauliZ
from main.codes.hexagonal.tic_tac_toe.TicTacToeCode import TicTacToeCode


class HoneycombCode(TicTacToeCode):
    def __init__(self, distance: int):
        tic_tac_toe = [
            (Red, PauliX),
            (Green, PauliY),
            (Blue, PauliZ)]
        super().__init__(distance, tic_tac_toe)
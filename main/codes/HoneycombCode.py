from main.Colour import Red, Green, Blue
from main.building_blocks.Pauli import PauliX, PauliY, PauliZ
from main.codes.TicTacToeCode import TicTacToeCode


class HoneycombCode(TicTacToeCode):
    def __init__(self, distance: int):
        tic_tac_toe = [
            (Red, PauliX),
            (Green, PauliY),
            (Blue, PauliZ)]
        super().__init__(distance, tic_tac_toe)
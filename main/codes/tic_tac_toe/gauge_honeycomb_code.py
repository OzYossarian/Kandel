from main.utils.Colour import Red, Green, Blue
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.gauge_tictactoe_code import GaugeTicTacToeCode


class GaugeHoneycombCode(GaugeTicTacToeCode):
    def __init__(self, distance: int):
        tic_tac_toe = [
            (Red, PauliLetter('X')),
            (Red, PauliLetter('X')),
            (Green, PauliLetter('Y')),
            (Green, PauliLetter('Y')),
            (Blue, PauliLetter('Z')),
            (Blue, PauliLetter('Z')),
            (Red, PauliLetter('X')),
            (Red, PauliLetter('X')),
            (Green, PauliLetter('Y')),
            (Green, PauliLetter('Y')),
            (Blue, PauliLetter('Z')),
            (Blue, PauliLetter('Z'))]
        super().__init__(distance, tic_tac_toe)

from main.codes.tic_tac_toe.gauge_floquet_tic_tac_toe_code import GaugeColourTicTacToeCode
from main.utils.Colour import Red, Green, Blue
from main.building_blocks.pauli.PauliLetter import PauliLetter


class GaugeFloquetColourCode(GaugeColourTicTacToeCode):
    """ Floquet colour code with repeated measuremnts of the same edges.
    """
    def __init__(self, distance: int, gauge_factor: int):
        tic_tac_toe= [
            (Red, PauliLetter('X')),
            (Green, PauliLetter('Z')),
            (Blue, PauliLetter('X')),
            (Red, PauliLetter('Z')),
            (Green, PauliLetter('X')),
            (Blue, PauliLetter('Z')),
        ]
        gauge_tic_tac_toe = []
        for _ in range(2):
            for edge in tic_tac_toe:
                gauge_tic_tac_toe.extend([edge] * gauge_factor)
       
        super().__init__(distance, gauge_tic_tac_toe, gauge_factor)

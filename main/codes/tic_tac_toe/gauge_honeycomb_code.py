from main.utils.Colour import Red, Green, Blue
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.gauge_tictactoe_code import GaugeTicTacToeCode


class GaugeHoneycombCode(GaugeTicTacToeCode):
    """ Honeycomb code with repeated measuremnts of the same edges.
    """
    def __init__(self, distance: int, gauge_factor: int):
        tic_tac_toe = [
            (Red, PauliLetter('X')),
            (Green, PauliLetter('Y')),
            (Blue, PauliLetter('Z'))]
        super().__init__(distance, tic_tac_toe, gauge_factor)
        #tic_tac_toe = []
#        for _ in range(2):
 #           for edge in [(Red, PauliLetter('X')), (Green, PauliLetter('Y')), 
         #                (Blue, PauliLetter('Z'))]:
          #      tic_tac_toe.extend([edge]* gauge_factor)
        
#        super().__init__(distance, tic_tac_toe, gauge_factor)
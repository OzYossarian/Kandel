from main.codes.tic_tac_toe.stability_observable.stability_logical_operator import StabilityOperator
from main.utils.Colour import Red, Green, Blue
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode


class HoneycombCode(TicTacToeCode):
    def __init__(self, distance: int):
        tic_tac_toe = [
            (Red, PauliLetter('X')),
            (Green, PauliLetter('Y')),
            (Blue, PauliLetter('Z'))]
        self.get_stability_observables()
        super().__init__(distance, tic_tac_toe)

    def get_stability_observables(self):
        self.x_stability_operator = StabilityOperator([2, 3, 4], self)
        self.z_stability_operator = StabilityOperator([5, 6, 7], self)

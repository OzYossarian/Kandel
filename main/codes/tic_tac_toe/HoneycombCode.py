from typing import List
from main.building_blocks.pauli import Pauli
from main.codes.tic_tac_toe.logical.TicTacToeLogicalOperator import TicTacToeLogicalOperator
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

    def get_possible_final_measurement(self, logical_operator: TicTacToeLogicalOperator,
                                       round: int) -> List[Pauli]:
        """Returns the final measurements required to measure a logical operator.

        This measurements returned implement a temporal domain wall to the trivial phase.
        There are two possible bosons that can be condensed to implement the domain wall 
        and obtain the value of the logical operator. Here one of the two bosons is chosen 
        to be condensed depending what logical_operator.at_round returns.        

        Args:
            logical_operator:
                The logical operator that needs to be measured.
            round:
                The index of the round that needs to be measured.

        Returns:
            List[Pauli]:
                A list of Pauli objects representing the final measurement.
        """
        logical_operator: List[Pauli]
        logical_operator = logical_operator.at_round(round)
        measurement_basis = logical_operator[0].letter.letter
        final_measurement = [Pauli(qubit, PauliLetter(measurement_basis))
                             for qubit in self.data_qubits.values()]
        return (final_measurement)

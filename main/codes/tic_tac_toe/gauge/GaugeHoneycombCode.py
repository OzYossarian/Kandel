from typing import List

from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.HoneycombCode import HoneycombCode
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.codes.tic_tac_toe.detectors.TicTacToeDrumBlueprint import TicTacToeDrumBlueprint
from main.codes.tic_tac_toe.gauge.GaugeTicTacToeCode import GaugeTicTacToeCode
from main.codes.tic_tac_toe.logical.TicTacToeLogicalOperator import TicTacToeLogicalOperator
from main.utils.Colour import Red, Green, Blue


class GaugeHoneycombCode(GaugeTicTacToeCode):
    def __init__(self, distance: int, gauge_factors: List[int]):
        """A gauge-fixed honeycomb code.

        Args:
            distance: The distance of the code.
            gauge_factors: A list containing the number of times each check is repeated.
                            Entry 1 means the check is repeated once, entry 2 means the check is repeated twice, etc.
        """
        assert len(gauge_factors) == 3
        self.rx_gf = gauge_factors[0]
        self.gy_gf = gauge_factors[1]
        self.bz_gf = gauge_factors[2]
        self.tic_tac_toe_route = [
            (Red, PauliLetter('X')) for _ in range(self.rx_gf)] + \
            [(Green, PauliLetter('Y')) for _ in range(self.gy_gf)] + \
            [(Blue, PauliLetter('Z')) for _ in range(self.bz_gf)]
        super().__init__(distance, gauge_factors)

    def get_ungauged_code(self, distance: int) -> TicTacToeCode:
        return HoneycombCode(distance)

    def get_plaquette_detector_schedule(self) -> List[List[Drum]]:
        # Rather than build the actual detectors from scratch, build the
        # blueprints, and let the ungauged code build the actual detectors.
        blue_z_drum_floor = [
            (self.rx_gf - 1, Red, PauliLetter('X')),
            (self.rx_gf + self.gy_gf - 1, Green, PauliLetter('Y'))]
        blue_z_drum_lid = [
            (2*self.rx_gf + self.gy_gf + self.bz_gf - 1, Red, PauliLetter('X')),
            (2*self.rx_gf + self.gy_gf + self.bz_gf, Green, PauliLetter('Y'))]
        blue_z_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            2*self.rx_gf + self.gy_gf + self.bz_gf,
            blue_z_drum_floor,
            blue_z_drum_lid)

        green_y_drum_floor = [
            (self.rx_gf + self.gy_gf + self.bz_gf - 1, Blue, PauliLetter('Z')),
            (2*self.rx_gf + self.gy_gf + self.bz_gf - 1, Red, PauliLetter('X'))]
        green_y_drum_lid = [
            (2*self.rx_gf + 2*self.gy_gf + 2 *
             self.bz_gf - 1, Blue, PauliLetter('Z')),
            (2*self.rx_gf + 2*self.gy_gf + 2*self.bz_gf, Red, PauliLetter('X'))]
        green_y_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            2*self.rx_gf + 2*self.gy_gf + 2*self.bz_gf,
            green_y_drum_floor,
            green_y_drum_lid)

        red_x_drum_floor = [
            (2*self.rx_gf + 2*self.gy_gf + self.bz_gf - 1, Green, PauliLetter('Y')),
            (2*self.rx_gf + 2*self.gy_gf + 2*self.bz_gf - 1, Blue, PauliLetter('Z'))]
        red_x_drum_lid = [
            (3*self.rx_gf + 3*self.gy_gf + 2 *
             self.bz_gf - 1, Green, PauliLetter('Y')),
            (3*self.rx_gf + 3*self.gy_gf + 2*self.bz_gf, Blue, PauliLetter('Z'))]
        red_x_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            3*self.rx_gf + 3*self.gy_gf + 2*self.bz_gf,
            red_x_drum_floor,
            red_x_drum_lid)

        blueprints = {
            Blue: [blue_z_drum_blueprint],
            Green: [green_y_drum_blueprint],
            Red: [red_x_drum_blueprint]}

        return self.ungauged_code.create_detectors(
            blueprints, self.schedule_length)

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

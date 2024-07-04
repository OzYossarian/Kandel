from typing import List

from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.HoneycombCode import HoneycombCode
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.codes.tic_tac_toe.detectors.TicTacToeDrumBlueprint import TicTacToeDrumBlueprint
from main.codes.tic_tac_toe.gauge.GaugeTicTacToeCode import GaugeTicTacToeCode
from main.utils.Colour import Red, Green, Blue


class GaugeHoneycombCode(GaugeTicTacToeCode):
    def __init__(self, distance: int, gauge_factor: int):
        super().__init__(distance, gauge_factor)

    def get_ungauged_code(self, distance: int) -> TicTacToeCode:
        return HoneycombCode(distance)

    def get_plaquette_detector_schedule(self) -> List[List[Drum]]:
        # Rather than build the actual detectors from scratch, build the
        # blueprints, and let the ungauged code build the actual detectors.
        blue_z_drum_floor = [
            (1 * self.gauge_factor - 1, Red, PauliLetter('X')),
            (2 * self.gauge_factor - 1, Green, PauliLetter('Y'))]
        blue_z_drum_lid = [
            (4 * self.gauge_factor - 1, Red, PauliLetter('X')),
            (4 * self.gauge_factor, Green, PauliLetter('Y'))]
        blue_z_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            4 * self.gauge_factor,
            blue_z_drum_floor,
            blue_z_drum_lid)

        green_y_drum_floor = [
            (3 * self.gauge_factor - 1, Blue, PauliLetter('Z')),
            (4 * self.gauge_factor - 1, Red, PauliLetter('X'))]
        green_y_drum_lid = [
            (6 * self.gauge_factor - 1, Blue, PauliLetter('Z')),
            (6 * self.gauge_factor, Red, PauliLetter('X'))]
        green_y_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            6 * self.gauge_factor,
            green_y_drum_floor,
            green_y_drum_lid)

        red_x_drum_floor = [
            (5 * self.gauge_factor - 1, Green, PauliLetter('Y')),
            (6 * self.gauge_factor - 1, Blue, PauliLetter('Z'))]
        red_x_drum_lid = [
            (8 * self.gauge_factor - 1, Green, PauliLetter('Y')),
            (8 * self.gauge_factor, Blue, PauliLetter('Z'))]
        red_x_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            8 * self.gauge_factor,
            red_x_drum_floor,
            red_x_drum_lid)

        blueprints = {
            Blue: [blue_z_drum_blueprint],
            Green: [green_y_drum_blueprint],
            Red: [red_x_drum_blueprint]}
        return self.ungauged_code.create_detectors(
            blueprints, self.schedule_length)

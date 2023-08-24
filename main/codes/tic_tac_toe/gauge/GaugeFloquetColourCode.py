from typing import List

from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.FloquetColourCode import FloquetColourCode
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.codes.tic_tac_toe.detectors.TicTacToeDrumBlueprint import TicTacToeDrumBlueprint
from main.codes.tic_tac_toe.gauge.GaugeTicTacToeCode import GaugeTicTacToeCode
from main.utils.Colour import Red, Green, Blue


class GaugeFloquetColourCode(GaugeTicTacToeCode):
    def __init__(self, distance: int, gauge_factor: int):
        super().__init__(distance, gauge_factor)

    def get_ungauged_code(self, distance: int) -> TicTacToeCode:
        return FloquetColourCode(distance)

    def get_plaquette_detector_schedule(self) -> List[List[Drum]]:
        # Rather than build the actual detectors from scratch, build the
        # blueprints, and let the ungauged code build the actual detectors.

        # Start with X detectors
        blue_x_drum_floor = [
            (1 * self.gauge_factor - 1, Red, PauliLetter('X'))]
        blue_x_drum_lid = [
            (4 * self.gauge_factor, Green, PauliLetter('X'))]
        blue_x_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            4 * self.gauge_factor,
            blue_x_drum_floor,
            blue_x_drum_lid)

        green_x_drum_floor = [
            (3 * self.gauge_factor - 1, Blue, PauliLetter('X'))]
        green_x_drum_lid = [
            (6 * self.gauge_factor, Red, PauliLetter('X'))]
        green_x_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            6 * self.gauge_factor,
            green_x_drum_floor,
            green_x_drum_lid)

        red_x_drum_floor = [
            (5 * self.gauge_factor - 1, Green, PauliLetter('X'))]
        red_x_drum_lid = [
            (8 * self.gauge_factor, Blue, PauliLetter('X'))]
        red_x_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            8 * self.gauge_factor,
            red_x_drum_floor,
            red_x_drum_lid)

        # Now do Z detectors
        red_z_drum_floor = [
            (2 * self.gauge_factor - 1, Green, PauliLetter('Z'))]
        red_z_drum_lid = [
            (5 * self.gauge_factor, Blue, PauliLetter('Z'))]
        red_z_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            5 * self.gauge_factor,
            red_z_drum_floor,
            red_z_drum_lid)

        blue_z_drum_floor = [
            (4 * self.gauge_factor - 1, Red, PauliLetter('Z'))]
        blue_z_drum_lid = [
            (7 * self.gauge_factor, Green, PauliLetter('Z'))]
        blue_z_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            7 * self.gauge_factor,
            blue_z_drum_floor,
            blue_z_drum_lid)

        green_z_drum_floor = [
            (6 * self.gauge_factor - 1, Blue, PauliLetter('Z'))]
        green_z_drum_lid = [
            (9 * self.gauge_factor, Red, PauliLetter('Z'))]
        green_z_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            9 * self.gauge_factor,
            green_z_drum_floor,
            green_z_drum_lid)

        blueprints = {
            Blue: [blue_x_drum_blueprint, blue_z_drum_blueprint],
            Green: [green_x_drum_blueprint, green_z_drum_blueprint],
            Red: [red_x_drum_blueprint, red_z_drum_blueprint]}
        return self.ungauged_code.create_detectors(
            blueprints, self.schedule_length)

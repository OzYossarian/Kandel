from typing import List

from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.FloquetColourCode import FloquetColourCode
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.codes.tic_tac_toe.detectors.TicTacToeDrumBlueprint import TicTacToeDrumBlueprint
from main.codes.tic_tac_toe.gauge.GaugeTicTacToeCode import GaugeTicTacToeCode
from main.codes.tic_tac_toe.stability_observable.stability_logical_operator import StabilityOperator
from main.utils.Colour import Red, Green, Blue
from main.building_blocks.pauli.PauliLetter import PauliLetter


class GaugeFloquetColourCode(GaugeTicTacToeCode):
    def __init__(self, distance: int, gauge_factors: List[int]):
        """A gauge-fixed Floquet colour code.

        Args:
            distance:
                The distance of the code.
            gauge_factors:
                A list containing the number of times each check is repeated. Entry 1 means the check is repeated once, entry 2 means the check is repeated twice, etc.
        """
        self.x_gf = gauge_factors[0]
        self.z_gf = gauge_factors[1]

        self.tic_tac_toe_route = [
            (Red, PauliLetter('X')) for _ in range(self.x_gf)] + \
            [(Green, PauliLetter('Z')) for _ in range(self.z_gf)] + \
            [(Blue, PauliLetter('X')) for _ in range(self.x_gf)] + \
            [(Red, PauliLetter('Z')) for _ in range(self.z_gf)] + \
            [(Green, PauliLetter('X')) for _ in range(self.x_gf)] + \
            [(Blue, PauliLetter('Z')) for _ in range(self.z_gf)]
        gauge_factors = [self.x_gf, self.z_gf, self.x_gf, self.z_gf,
                         self.x_gf, self.z_gf]
        self.get_stability_observables()

        super().__init__(distance, gauge_factors)
        self.get_plaquette_detector_schedule()

    def get_stability_observables(self):
        self.x_stability_operator = StabilityOperator(
            [self.x_gf+self.z_gf, 2*self.x_gf + 2*self.z_gf], self)
        self.z_stability_operator = StabilityOperator(
            [2*self.x_gf+self.z_gf, 3*self.x_gf+2*self.z_gf], self)

    def get_ungauged_code(self, distance: int) -> TicTacToeCode:
        return FloquetColourCode(distance)

    def get_plaquette_detector_schedule(self) -> List[List[Drum]]:
        # Rather than build the actual detectors from scratch, build the
        # blueprints, and let the ungauged code build the actual detectors.
        blue_x_drum_floor = [
            (1 * self.x_gf - 1, Red, PauliLetter('X'))]
        blue_x_drum_lid = [
            (2 * self.x_gf + 2 * self.z_gf, Green, PauliLetter('X'))]
        blue_x_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            2 * self.x_gf + 2 * self.z_gf,
            blue_x_drum_floor,
            blue_x_drum_lid)

        green_x_drum_floor = [
            (2 * self.x_gf + self.z_gf - 1, Blue, PauliLetter('X'))]
        green_x_drum_lid = [
            (3 * self.x_gf + 3 * self.z_gf, Red, PauliLetter('X'))]
        green_x_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            3 * self.x_gf + 3 * self.z_gf,
            green_x_drum_floor,
            green_x_drum_lid)

        red_x_drum_floor = [
            (3 * self.x_gf + 2 * self.z_gf - 1, Green, PauliLetter('X'))]
        red_x_drum_lid = [
            (4 * self.x_gf + 4 * self.z_gf, Blue, PauliLetter('X'))]
        red_x_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            4 * self.x_gf + 4 * self.z_gf,
            red_x_drum_floor,
            red_x_drum_lid)

        red_z_drum_floor = [
            (self.x_gf + self.z_gf - 1, Green, PauliLetter('Z'))]
        red_z_drum_lid = [
            (3*self.x_gf + 2*self.z_gf, Blue, PauliLetter('Z'))]
        red_z_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            3*self.x_gf + 2*self.z_gf,
            red_z_drum_floor,
            red_z_drum_lid)

        blue_z_drum_floor = [
            (2 * self.x_gf + 2 * self.z_gf - 1, Red, PauliLetter('Z'))]
        blue_z_drum_lid = [
            (4 * self.x_gf + 3*self.z_gf, Green, PauliLetter('Z'))]
        blue_z_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            4 * self.x_gf + 3 * self.z_gf,
            blue_z_drum_floor,
            blue_z_drum_lid)

        green_z_drum_floor = [
            (3 * self.x_gf + 3 * self.z_gf - 1, Blue, PauliLetter('Z'))]
        green_z_drum_lid = [
            (5 * self.x_gf + 4 * self.z_gf, Red, PauliLetter('Z'))]
        green_z_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            5 * self.x_gf + 4 * self.z_gf,
            green_z_drum_floor,
            green_z_drum_lid)

        blueprints = {
            Blue: [blue_x_drum_blueprint, blue_z_drum_blueprint],
            Green: [green_x_drum_blueprint, green_z_drum_blueprint],
            Red: [red_x_drum_blueprint, red_z_drum_blueprint]}
        return self.ungauged_code.create_detectors(
            blueprints, self.schedule_length)

    @staticmethod
    def count_letter_with_skip(list_of_letters, letter):
        count = 0
        skip_next = True
        matched = False

        for l in list_of_letters:
            if l == letter:
                if not skip_next:
                    count += 1
                matched = True

            else:
                if matched == True:
                    skip_next = not skip_next

                matched = False
        return count

    @staticmethod
    def count_letter(list_of_letters, letter):
        count = 0
        matched = False
        for l in list_of_letters:

            if l == letter:
                if matched == False:
                    count += 1
                    matched = True
            else:
                matched = False
        return count

    @staticmethod
    def repeat_list_to_length(original_list, x):
        repeated_list = (original_list * (x // len(original_list) + 1))[:x]
        return repeated_list

    def get_measurement_error_distance(self, rounds, letter):
        """error index: is the error on the 'X' or 'Z' measuerements!
        """
        measurement_pattern = [
            edge[1].letter for edge in self.tic_tac_toe_route]
        measurement_pattern = self.repeat_list_to_length(
            measurement_pattern, rounds)
        letter_count = self.count_letter_with_skip(measurement_pattern, letter)
        return (letter_count)

    def get_pauli_error_distance(self, rounds, letter):
        """error index: is the error on the 'X' or 'Z' measuerements!
        """
        measurement_pattern = [
            edge[1].letter for edge in self.tic_tac_toe_route]
        measurement_pattern = self.repeat_list_to_length(
            measurement_pattern, rounds)

        letter_count = self.count_letter(
            measurement_pattern[(self.x_gf + self.z_gf):], letter)
        return (letter_count)

    def get_number_of_rounds_for_stability_experiment(self, desired_distance):
        #TODO
        """Get the minimal number of rounds needed to perform a stability experiment of distance d"""
        n_rounds = len(self.tic_tac_toe_route)
        print(n_rounds)
#        while actual
        pass

    def get_distance_stability_experiment(self, rounds, letter):
        return (min(self.get_pauli_error_distance(rounds, letter), self.get_measurement_error_distance(rounds, letter)))

import json
from pathlib import Path
from typing import List, Literal, Tuple, Union

from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.FloquetColourCode import FloquetColourCode
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.codes.tic_tac_toe.detectors.TicTacToeDrumBlueprint import TicTacToeDrumBlueprint
from main.codes.tic_tac_toe.gauge.GaugeTicTacToeCode import GaugeTicTacToeCode
from main.codes.tic_tac_toe.logical.TicTacToeLogicalOperator import TicTacToeLogicalOperator
from main.codes.tic_tac_toe.stability_observable.stability_logical_operator import StabilityOperator
from main.utils.Colour import Red, Green, Blue
from main.building_blocks.pauli.PauliLetter import PauliLetter


class GaugeFloquetColourCode(GaugeTicTacToeCode):
    def __init__(self, distance: Union[int, List[int]], gauge_factors: List[int]):
        self.x_gf, self.z_gf = gauge_factors
        self.tic_tac_toe_route = self.create_tic_tac_toe_route()
        gauge_factors = [self.x_gf, self.z_gf, self.x_gf, self.z_gf,
                         self.x_gf, self.z_gf]
        self.get_stability_observables()
        super().__init__(distance, gauge_factors)
        self.get_plaquette_detector_schedule()

    def create_tic_tac_toe_route(self):
        route = []
        for color, letter in [(Red, 'X'), (Green, 'Z'), (Blue, 'X'), (Red, 'Z'), (Green, 'X'), (Blue, 'Z')]:
            route.extend([(color, PauliLetter(letter))
                         for _ in range(self.x_gf if letter == 'X' else self.z_gf)])
        return route

    def get_stability_observables(self):
        self.x_stability_operator = StabilityOperator(
            [self.x_gf + self.z_gf, 2 * self.x_gf + 2 * self.z_gf], self)
        self.z_stability_operator = StabilityOperator(
            [2 * self.x_gf + self.z_gf, 3 * self.x_gf + 2 * self.z_gf], self)

    def get_ungauged_code(self, distance: int) -> TicTacToeCode:
        return FloquetColourCode(distance)

    def get_plaquette_detector_schedule(self) -> List[List[Drum]]:
        def create_blueprint(floor, lid, length):
            return TicTacToeDrumBlueprint(self.schedule_length, length, floor, lid)

        blueprints = {
            Blue: [
                create_blueprint([(1 * self.x_gf - 1, Red, PauliLetter('X'))], [
                                 (2 * self.x_gf + 2 * self.z_gf, Green, PauliLetter('X'))], 2 * self.x_gf + 2 * self.z_gf),
                create_blueprint([(2 * self.x_gf + 2 * self.z_gf - 1, Red, PauliLetter('Z'))], [
                                 (4 * self.x_gf + 3 * self.z_gf, Green, PauliLetter('Z'))], 4 * self.x_gf + 3 * self.z_gf)
            ],
            Green: [
                create_blueprint([(2 * self.x_gf + self.z_gf - 1, Blue, PauliLetter('X'))], [
                                 (3 * self.x_gf + 3 * self.z_gf, Red, PauliLetter('X'))], 3 * self.x_gf + 3 * self.z_gf),
                create_blueprint([(3 * self.x_gf + 3 * self.z_gf - 1, Blue, PauliLetter('Z'))], [
                                 (5 * self.x_gf + 4 * self.z_gf, Red, PauliLetter('Z'))], 5 * self.x_gf + 4 * self.z_gf)
            ],
            Red: [
                create_blueprint([(3 * self.x_gf + 2 * self.z_gf - 1, Green, PauliLetter('X'))], [
                                 (4 * self.x_gf + 4 * self.z_gf, Blue, PauliLetter('X'))], 4 * self.x_gf + 4 * self.z_gf),
                create_blueprint([(self.x_gf + self.z_gf - 1, Green, PauliLetter('Z'))], [
                                 (3 * self.x_gf + 2 * self.z_gf, Blue, PauliLetter('Z'))], 3 * self.x_gf + 2 * self.z_gf)
            ]
        }
        return self.ungauged_code.create_detectors(blueprints, self.schedule_length)

    @staticmethod
    def count_letter_with_skip(list_of_letters, letter):
        """Counts the number of times a letter appears in a list, skipping every other occurrence after the first match.

        Args:
            list_of_letters (List[str]): The list of letters to search through.
            letter (str): The letter to count in the list.

        Returns:
            int: The count of the specified letter in the list, skipping every other occurrence after the first match.
        """
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
    def count_letter(list_of_letters: List[str], letter: str) -> int:
        """Counts the number of times a letter appears in a list, considering consecutive occurrences as one.

        Args:
            list_of_letters (List[str]): The list of letters to search through.
            letter (str): The letter to count in the list.

        Returns:
            int: The count of the specified letter in the list, considering consecutive occurrences as one.
        """
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
    def repeat_list_to_length(original_list: List, desired_length: int) -> List:
        """Repeats a list until it reaches a certain length."""
        repeated_list = (original_list * (desired_length //
                         len(original_list) + 1))[:desired_length]
        return repeated_list

    def get_measurement_error_distance(self, rounds: int, letter: Literal['X', 'Z']) -> int:
        """Returns the minimum weight of a timelike logical consisting of measurement errors.

        For an 'X' ('Z') stability experiment this weight (distance) can be calculated from looking at
        how often the letter 'X' ('Z') appears in the measurement pattern.

        Args:
            rounds: The number of rounds in the experiment.
            letter: The letter of the stability experiment to get the distance of.

        Returns:
            int: The distance of the stability experiment.
        """
        measurement_pattern = [
            edge[1].letter for edge in self.tic_tac_toe_route]
        measurement_pattern = self.repeat_list_to_length(
            measurement_pattern, rounds)
        measurement_error_distance = self.count_letter_with_skip(
            measurement_pattern, letter)
        return (measurement_error_distance)

    def get_possible_final_measurement(self, logical_operator: TicTacToeLogicalOperator, rounds: int) -> List[Tuple[int, StabilityOperator]]:
        measurement_basis = logical_operator.logical_letter.letter

        final_measurement = [Pauli(qubit, PauliLetter(measurement_basis))
                             for qubit in self.data_qubits.values()]
        return final_measurement

    def get_pauli_error_distance(self, rounds: int, letter: Literal['X', 'Z']) -> int:
        """Returns the minimum weight of a timelike logical consisting of X,Y, or Z errors on
        data qubits.

        For an 'X' ('Z') stability experiment this weight (distance) can be calculated from looking at
        how often the letter 'X' ('Z') appears in the measurement pattern.

        Args:
            rounds: The number of rounds in the experiment.
            letter: The letter of the stability experiment to get the distance of.

        Returns:
            int: The distance of the stability experiment.
        """
        measurement_pattern = [
            edge[1].letter for edge in self.tic_tac_toe_route]
        measurement_pattern = self.repeat_list_to_length(
            measurement_pattern, rounds)

        pauli_error_distance = self.count_letter(
            measurement_pattern[(self.x_gf + self.z_gf):], letter)
        return (pauli_error_distance)

    def get_number_of_rounds_for_timelike_distance(self,
                                                   desired_distance: int,
                                                   graphlike: bool = False,
                                                   noise_model: str = "phenomenological") -> Tuple[int, int, int]:
        """Get the minimal number of rounds needed to perform a stability experiment

        This method assumes a phenmenological noise model is used. The number of rounds
        is returned such that both the distance of x and z stability experiments are at least the
        desired_distance. Distance here refers to the minimum number of errors needed to create
        a timelike logical operator.

        Args:
            desired_distance (int): The desired distance for the stability experiment

        Returns:
            Tuple[int, int, int]: A tuple containing:
                - The number of rounds needed to perform a stability experiment
                - The distance of the x-stability experiment with the given number of rounds
                - The distance of the z-stability experiment with the given number of rounds

        """
        n_rounds = len(self.tic_tac_toe_route)
        distance_x = self.get_graphlike_timelike_distance(
            n_rounds, 'X', noise_model)

        distance_z = self.get_graphlike_timelike_distance(
            n_rounds, 'Z', noise_model)

        while min(distance_x, distance_z) < desired_distance:
            n_rounds += 1
            distance_x = self.get_graphlike_timelike_distance(
                n_rounds, 'X', noise_model)

            distance_z = self.get_graphlike_timelike_distance(
                n_rounds, 'Z', noise_model)

        return n_rounds, distance_x, distance_z

    def get_boundary_and_bulk_layers(self, n_rounds):
        bulk_length = 6 * (self.gauge_factors[0] + self.gauge_factors[1])
        bulk_layers = n_rounds//bulk_length
        boundary_layers = n_rounds % bulk_length
        return boundary_layers, bulk_layers - 1

    def distance_from_timelike_distance_dict(self, n_rounds: int, pauli_letter: Literal['X', 'Z'], timelike_distance_dict: dict) -> int:
        """ Returns the timelike distance of the code using precalculated data.

        Args:
            n_rounds (int): The number of measurement rounds.
            pauli_letter (Literal['X', 'Z']): The type of stability experiment ('X' or 'Z').
            timelike_distance_dict (dict): The precalculated data.

        Returns:
            int: The timelike distance of the code.
        """
        # the distance is calculated in two steps, the distance of the boundary layers
        # and the distance of the bulk layers. This is done so that the distance for
        # any number of rounds can be calculated, because the bulk layers are repeated.
        boundary_layers, bulk_layers = self.get_boundary_and_bulk_layers(
            n_rounds)
        td_boundary = timelike_distance_dict[pauli_letter][
            f"({self.gauge_factors[0]}, {self.gauge_factors[1]})"]['td_boundary'][str(boundary_layers)]
        td_bulk = timelike_distance_dict[pauli_letter][f"({self.gauge_factors[0]}, {self.gauge_factors[1]})"
                                                       ]['td_bulk'] * bulk_layers
        return td_boundary + td_bulk

    def get_number_of_rounds_for_single_timelike_distance(self, desired_distance: int, pauli_letter: Literal['X', 'Z'], graphlike=False, noise_model="phenomenological_noise") -> int:
        n_rounds = len(self.tic_tac_toe_route)

        if graphlike == False:
            distance_func = self.get_non_graphlike_timelike_distance
        else:
            distance_func = self.get_graphlike_timelike_distance

        distance = distance_func(n_rounds, pauli_letter, noise_model)

        while distance < desired_distance:
            n_rounds += 1
            distance = distance_func(n_rounds, pauli_letter, noise_model)
        return n_rounds

    def get_non_graphlike_timelike_distance(self, n_rounds: int, pauli_letter: Literal['X', 'Z'], noise_model="phenoenological_noise") -> int:
        """ Returns the distance of the code if one uses a correlated decoder using precalculated data.

        The data has been generated by running the script create_non_graphlike_timelike_distance_data.py

        Args:
            n_rounds (int): The number of measurement rounds.
            pauli_letter (Literal['X', 'Z']): The type of stability experiment ('X' or 'Z').

        Returns:
            int: The timelike distance of the code.
        """
        if noise_model == "phenomenological_noise":
            p = Path(__file__).parent / 'new_timelike_distance_data' / \
                'fcc_non_graphlike_td_data_phenomenological.json'
        elif noise_model == "circuit_level_noise":
            p = Path(__file__).parent / 'new_timelike_distance_data' / \
                'fcc_non_graphlike_td_data_circuit_level_depolarizing.json'
        elif noise_model == "EM3":
            p = Path(__file__).parent / 'new_timelike_distance_data' / \
                'fcc_non_graphlike_td_data_EM3.json'
        with p.open('r') as openfile:
            timelike_distance_dict = json.load(openfile)
        return (self.distance_from_timelike_distance_dict(n_rounds, pauli_letter, timelike_distance_dict))
    
    def get_graphlike_timelike_distance(self, n_rounds: int, pauli_letter: Literal['X', 'Z'], noise_model) -> int:
        """ Returns the distance of the code if one decodes using a matching decoder.

        Args:
            n_rounds (int): The number of measurement rounds.
            pauli_letter (Literal['X', 'Z']): The type of stability experiment ('X' or 'Z').

        Returns:
            int: The timelike distance of the code.
        """

        if noise_model == "phenomenological_noise":
            p = Path(__file__).parent / 'new_timelike_distance_data' / \
                'fcc_graphlike_td_data_phenomenological.json'

        elif noise_model == "circuit_level_noise":
            p = Path(__file__).parent / 'new_timelike_distance_data' / \
                'fcc_graphlike_td_data_circuit_level_depolarizing.json'

        elif noise_model == "EM3":
            p = Path(__file__).parent / 'new_timelike_distance_data' / \
                'fcc_graphlike_td_data_EM3.json'
        with p.open('r') as openfile:
            timelike_distance_dict = json.load(openfile)
        return (self.distance_from_timelike_distance_dict(n_rounds, pauli_letter, timelike_distance_dict))

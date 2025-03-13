import json
from typing import List, Literal, Tuple, Union
from pathlib import Path

from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.HoneycombCode import HoneycombCode
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.codes.tic_tac_toe.detectors.TicTacToeDrumBlueprint import TicTacToeDrumBlueprint
from main.codes.tic_tac_toe.gauge.GaugeTicTacToeCode import GaugeTicTacToeCode
from main.codes.tic_tac_toe.stability_observable.stability_logical_operator import StabilityOperator
from main.codes.tic_tac_toe.logical.TicTacToeLogicalOperator import TicTacToeLogicalOperator
from main.utils.Colour import Red, Green, Blue


class GaugeHoneycombCode(GaugeTicTacToeCode):
    def __init__(self, distance: Union[int, List[int]],
                 gauge_factors: List[int]):
        """A gauge-fixed honeycomb code.

        Args:
            distance: The distance of the code.
            gauge_factors: A list containing the number of times each check is repeated.
                            Entry 1 means the check is repeated once, entry 2 means the check is repeated twice, etc.
            create_e_detectors: Whether to create E-type detectors. 
            create_m_detectors: Whether to create M-type detectors.
        """
        assert len(gauge_factors) == 3
        self.rx_gf = gauge_factors[0]
        self.gy_gf = gauge_factors[1]
        self.bz_gf = gauge_factors[2]
        self.tic_tac_toe_route = [
            (Red, PauliLetter('X')) for _ in range(self.rx_gf)] + \
            [(Green, PauliLetter('Y')) for _ in range(self.gy_gf)] + \
            [(Blue, PauliLetter('Z')) for _ in range(self.bz_gf)]
        self.get_stability_observables()
        super().__init__(distance, gauge_factors)

    def get_stability_observables(self):
        self.x_stability_operator = StabilityOperator(
            [self.rx_gf+self.gy_gf,
             self.rx_gf+self.gy_gf+self.bz_gf,
             2*self.rx_gf+self.gy_gf+self.bz_gf], self)
        self.z_stability_operator = StabilityOperator(
            [2*self.rx_gf+2*self.gy_gf+self.bz_gf,
             2*self.rx_gf+2*self.gy_gf+2*self.bz_gf,
             3*self.rx_gf+2*self.gy_gf+2*self.bz_gf], self)

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

    def get_boundary_and_bulk_layers(self, n_rounds):
        bulk_length = 4 * sum(self.gauge_factors)
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
            f"({self.gauge_factors[0]}, {self.gauge_factors[1]}, {self.gauge_factors[2]})"]['td_boundary'][str(boundary_layers)]
        td_bulk = timelike_distance_dict[pauli_letter][f"({self.gauge_factors[0]}, {self.gauge_factors[1]}, {self.gauge_factors[2]})"
                                                       ]['td_bulk'] * bulk_layers
        return td_boundary + td_bulk

    def get_non_graphlike_timelike_distance(self, n_rounds: int, pauli_letter: Literal['X', 'Z'], noise_model) -> int:
        """ Returns the distance of the code if one uses a correlated decoder using precalculated data.

        The data has been generated by running the script create_non_graphlike_timelike_distance_data.py

        Args:
            n_rounds (int): The number of measurement rounds.
            pauli_letter (Literal['X', 'Z']): The type of stability experiment ('X' or 'Z').

        Returns:
            int: The timelike distance of the code.
        """
        if noise_model == "phenomenological_noise":
            p = Path(__file__).parent / 'timelike_distance_data' / \
                'hcc_non_graphlike_td_data_phenomenological.json'
        elif noise_model == "circuit_level_noise":
            p = Path(__file__).parent / 'timelike_distance_data' / \
                'hcc_non_graphlike_td_data_circuit_level_depolarizing.json'
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
            p = Path(__file__).parent / 'timelike_distance_data' / \
                'hcc_graphlike_td_data_phenomenological.json'
        elif noise_model == "circuit_level_noise":
            p = Path(__file__).parent / 'timelike_distance_data' / \
                'hcc_graphlike_td_data_circuit_level_depolarizing.json'
        elif noise_model == "EM3":
            p = Path(__file__).parent / 'timelike_distance_data' / \
                'hcc_graphlike_td_data_EM3.json'
        with p.open('r') as openfile:
            timelike_distance_dict = json.load(openfile)
        return (self.distance_from_timelike_distance_dict(n_rounds, pauli_letter, timelike_distance_dict))

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

    def get_number_of_rounds_for_timelike_distance(self, desired_distance: int, graphlike=False, noise_model="phenomenological_noise") -> Tuple[int, int, int]:
        """Get the minimal number of rounds needed to perform a stability experiment 

        This method assumes a phenmenological noise model is used. The number of rounds 
        is returned such that both the distance of x and z stability experiments are at least the 
        desired_distance. Distance here refers to the minimum number of errors needed to create 
        a timelike logical operator.

        Args:
            desired_distance (int): The desired distance for the stability experiment
            graphlike (bool, optional): Whether to use the graphlike timelike distance. Defaults to False.


        Returns:
            Tuple[int, int, int]: A tuple containing:
                - The number of rounds needed to perform a stability experiment
                - The distance of the x-stability experiment with the given number of rounds
                - The distance of the z-stability experiment with the given number of rounds
        """
        n_rounds = len(self.tic_tac_toe_route)

        if graphlike == False:
            distance_func = self.get_non_graphlike_timelike_distance
        else:
            distance_func = self.get_graphlike_timelike_distance

        distance_x = distance_func(n_rounds, 'X', noise_model)
        distance_z = distance_func(n_rounds, 'Z', noise_model)

        while min(distance_x, distance_z) < desired_distance:
            n_rounds += 1
            distance_x = distance_func(n_rounds, 'X', noise_model)
            distance_z = distance_func(n_rounds, 'Z', noise_model)

        return n_rounds, distance_x, distance_z

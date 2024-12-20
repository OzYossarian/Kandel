from abc import ABC, abstractmethod
from typing import List, Tuple

from main.building_blocks.detectors.Drum import Drum
from main.codes.ToricHexagonalCode import ToricHexagonalCode
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.Check import Check
from main.codes.tic_tac_toe.detectors.TicTacToeDrumBlueprint import TicTacToeDrumBlueprint
from main.utils.Colour import Red, Green, Blue
from main.utils.utils import coords_mid, xor, coords_minus, embed_coords


class GaugeTicTacToeCode(ABC, ToricHexagonalCode):
    def __init__(self, distance: int, gauge_factors: List[int]):
        # NOTE - haven't figured out a general way of repeating measurements
        # for any tic-tac-toe code. Have only done this for honeycomb code
        # and Floquet colour code. Hence this class is abstract, and just
        # contains the code common to GaugeHoneycombCode and
        # GaugeFloquetColourCode
        #        TODO
        if any(gauge_factor < 1 for gauge_factor in gauge_factors):
            raise ValueError("Gauge factor must be a positive integer.")

        rows = 3 * (distance // 4)
        columns = 4 * (distance // 4)

        # Start with an "ungauged" honeycomb code,
        # then edit the checks and detectors to get the gauged version.
        self.ungauged_code = self.get_ungauged_code(distance)
        if len(gauge_factors) != self.ungauged_code.schedule_length:
            raise ValueError(
                "The number of gauge factors must match the schedule length of the ungauged code."
            )

        super().__init__(
            rows=rows,
            columns=columns,
            distance=distance)
        self.data_qubits = self.ungauged_code.data_qubits
        self.gauge_factors = gauge_factors

        # Repeat each check the desired number of times
        self.schedule_length = sum(gauge_factors)
        # self.ungauged_code.schedule_length * gauge_factor
        check_schedule = []
        for gf_index, gauge_factor in enumerate(gauge_factors):
            for _ in range(gauge_factor):
                check_schedule.append(
                    self.ungauged_code.check_schedule[gf_index])

        # Create the small detectors
        detector_schedule: List[List[Drum]] = [
            [] for _ in range(self.schedule_length)]

        for ungauged_round, checks in enumerate(self.ungauged_code.check_schedule):
            for check in checks:
                for g in range(gauge_factors[ungauged_round]-1):
                    gauged_round = sum(gauge_factors[:ungauged_round]) + g + 1
                    detector = Drum([(-1, check)], [(0, check)], gauged_round)
                    detector_schedule[gauged_round].append(detector)

        # Create the plaquette detectors
        plaquette_detector_schedule = self.get_plaquette_detector_schedule()
        for round, detectors in enumerate(plaquette_detector_schedule):
            detector_schedule[round].extend(detectors)

        # Put it all together
        self.set_schedules(check_schedule, detector_schedule)

        # Tell the logical operators about the gauge factor.
        self.logical_qubits = self.ungauged_code.logical_qubits
        for logical_qubit in self.logical_qubits:
            for logical_operator in logical_qubit.operators:
                if logical_operator is not None:
                    logical_operator.gauge_factors = self.gauge_factors

        # check_schedule = [
        #    self.ungauged_code.check_schedule[round // gauge_factor]
        #    for round in range(self.schedule_length)]

        self.final_check_schedule = None

    @abstractmethod
    def get_ungauged_code(self, distance: int) -> TicTacToeCode:
        pass

    @abstractmethod
    def get_plaquette_detector_schedule(self) -> List[List[Drum]]:
        pass

    @abstractmethod
    def get_number_of_rounds_for_timelike_distance(self, desired_distance: int, graphlike=False) -> Tuple[int, int, int]:
        pass

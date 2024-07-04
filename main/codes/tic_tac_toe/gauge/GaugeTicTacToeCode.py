from abc import ABC, abstractmethod
from typing import List

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
    def __init__(self, distance: int, gauge_factor: int):
        # NOTE - haven't figured out a general way of repeating measurements
        # for any tic-tac-toe code. Have only done this for honeycomb code
        # and Floquet colour code. Hence this class is abstract, and just
        # contains the code common to GaugeHoneycombCode and
        # GaugeFloquetColourCode

        if gauge_factor < 1:
            raise ValueError("Gauge factor must be a positive integer.")
        rows = 3 * (distance // 4)
        columns = 4 * (distance // 4)
        # Start with an "ungauged" honeycomb code,
        # then edit the checks and detectors to get the gauged version.
        self.ungauged_code = self.get_ungauged_code(distance)
        super().__init__(
            rows=rows,
            columns=columns,
            distance=distance)
        self.data_qubits = self.ungauged_code.data_qubits
        self.gauge_factor = gauge_factor

        # Repeat each check the desired number of times
        self.schedule_length = self.ungauged_code.schedule_length * gauge_factor
        check_schedule = [
            self.ungauged_code.check_schedule[round // gauge_factor]
            for round in range(self.schedule_length)]

        # Create the small detectors
        detector_schedule: List[List[Drum]] = [
            [] for _ in range(self.schedule_length)]

        for ungauged_round, checks in enumerate(self.ungauged_code.check_schedule):
            for check in checks:
                for g in range(gauge_factor - 1):
                    gauged_round = ungauged_round * gauge_factor + g + 1
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
                    logical_operator.gauge_factor = self.gauge_factor

        check_schedule = [
            self.ungauged_code.check_schedule[round // gauge_factor]
            for round in range(self.schedule_length)]    
    
        self.final_check_schedule = None 

    @abstractmethod
    def get_ungauged_code(self, distance: int) -> TicTacToeCode:
        pass

    @abstractmethod
    def get_plaquette_detector_schedule(self) -> List[List[Drum]]:
        pass

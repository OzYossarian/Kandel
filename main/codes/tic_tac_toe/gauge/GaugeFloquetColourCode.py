from typing import List

from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.FloquetColourCode import FloquetColourCode
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.codes.tic_tac_toe.detectors.TicTacToeDrumBlueprint import TicTacToeDrumBlueprint
from main.codes.tic_tac_toe.gauge.GaugeTicTacToeCode import GaugeTicTacToeCode
from main.utils.Colour import Red, Green, Blue
from main.utils.utils import coords_mid, xor, coords_minus, embed_coords
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.building_blocks.Check import Check


class GaugeFloquetColourCode(GaugeTicTacToeCode):
    def __init__(self, distance: int, gauge_factors: List[int], boundary_repetitions: str = 'single'):
        """A gauge-fixed Floquet colour code.

        Args:
            distance: The distance of the code.
            gauge_factors: A list containing the number of times each check is repeated.
            boundary_type: The number of edge measurents to do at the boundary. Can be single, double or triple.
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
        super().__init__(distance, gauge_factors)
        if boundary_repetitions == 'single':
            self.get_plaquette_detector_schedule()
        elif boundary_repetitions == 'double':
            self.set_double_final_detector_schedule()
        elif boundary_repetitions == 'triple':
            self.set_triple_final_detector_schedule()

    def set_triple_final_detector_schedule(self):

        self.final_detector_schedule: List[List[Drum]] = [
            [] for _ in range(4)]
        self.final_detector_schedule[0].extend(self.detector_schedule[0])

        # red detectors
        red_x_drum_floor = [
            (5 * self.gauge_factor - 1, Green, PauliLetter('X'))]
        red_x_drum_lid = [
            (self.schedule_length + 1, Blue, PauliLetter('X'))]
        red_x_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            self.schedule_length + 1,
            red_x_drum_floor,
            red_x_drum_lid)

        anchors = self.colourful_plaquette_anchors[Red]
        detectors = []
        for anchor in anchors:
            # Create an actual detector object from each blueprint.
            floor, lid = [], []
            for (t, edge_colour, edge_letter) in red_x_drum_blueprint.floor:
                checks = self.ungauged_code.borders[anchor][(
                    edge_colour, edge_letter)]
                floor.extend((t, check) for check in checks)
            for (t, edge_colour, edge_letter) in red_x_drum_blueprint.lid:
                checks = self.ungauged_code.borders[anchor][(
                    edge_colour, edge_letter)]
                lid.extend((t, check) for check in checks)
            drum_anchor = embed_coords(anchor, 3)
            detectors.append(Drum(floor, lid, 0, drum_anchor))
            # ok so the anchor is the
        self.final_detector_schedule[1].extend(detectors)

        # blue detectors
        blue_x_drum_floor = [
            (5*self.gauge_factor + self.gauge_factor, Red, PauliLetter('X'))]
        blue_x_drum_lid = [
            (self.schedule_length + 2, Green, PauliLetter('X'))]
        blue_x_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            self.schedule_length + 2,
            blue_x_drum_floor,
            blue_x_drum_lid)

        anchors = self.colourful_plaquette_anchors[Blue]
        detectors = []
        for anchor in anchors:
            # Create an actual detector object from each blueprint.
            floor, lid = [], []
            for (t, edge_colour, edge_letter) in blue_x_drum_blueprint.floor:
                checks = self.ungauged_code.borders[anchor][(
                    edge_colour, edge_letter)]
                floor.extend((t, check) for check in checks)
            for (t, edge_colour, edge_letter) in blue_x_drum_blueprint.lid:
                checks = self.ungauged_code.borders[anchor][(
                    edge_colour, edge_letter)]
                lid.extend((t, check) for check in checks)
            drum_anchor = embed_coords(anchor, 3)
            detectors.append(Drum(floor, lid, 0, drum_anchor))
        self.final_detector_schedule[2].extend(detectors)

        data_qubits = self.data_qubits.values()
        final_measurements = [Pauli(qubit, PauliLetter("X"))
                              for qubit in data_qubits]
        qubit_check_dic = dict()
        final_checks = []
        for pauli in final_measurements:
            check = Check([pauli], pauli.qubit.coords)
            final_checks.append(check)
            qubit_check_dic[pauli.qubit] = check

        self.final_check_schedule = [self.ungauged_code.check_schedule[0],
                                     self.ungauged_code.check_schedule[2], self.ungauged_code.check_schedule[4], final_checks]

        # add the small detectors at the end!
        final_detectors = []
        for check in (self.final_check_schedule[-4]):
            qubits = list(check.paulis.values())
            check_lid_0 = qubit_check_dic[qubits[0].qubit]
            check_lid_1 = qubit_check_dic[qubits[1].qubit]
            final_detectors.append(
                Drum([(-3, check)], [(0, check_lid_0), (0, check_lid_1)], 2))

        for check in (self.final_check_schedule[-3]):
            qubits = list(check.paulis.values())
            check_lid_0 = qubit_check_dic[qubits[0].qubit]
            check_lid_1 = qubit_check_dic[qubits[1].qubit]
            final_detectors.append(
                Drum([(-2, check)], [(0, check_lid_0), (0, check_lid_1)], 2))

        for check in (self.final_check_schedule[-2]):
            qubits = list(check.paulis.values())
            check_lid_0 = qubit_check_dic[qubits[0].qubit]
            check_lid_1 = qubit_check_dic[qubits[1].qubit]
            final_detectors.append(
                Drum([(-1, check)], [(0, check_lid_0), (0, check_lid_1)], 2))

        self.final_detector_schedule[3].extend(final_detectors)

    def set_double_final_detector_schedule(self):
        # let's first make this work for any gauge factor

        self.final_detector_schedule: List[List[Drum]] = [
            [] for _ in range(3)]
        self.final_detector_schedule[0].extend(self.detector_schedule[0])
        red_x_drum_floor = [
            (5 * self.gauge_factor - 1, Green, PauliLetter('X'))]
        red_x_drum_lid = [
            (self.schedule_length + 1, Blue, PauliLetter('X'))]
        red_x_drum_blueprint = TicTacToeDrumBlueprint(
            self.schedule_length,
            self.schedule_length + 1,
            red_x_drum_floor,
            red_x_drum_lid)

        anchors = self.colourful_plaquette_anchors[Red]
        detectors = []
        for anchor in anchors:
            # Create an actual detector object from each blueprint.
            floor, lid = [], []
            for (t, edge_colour, edge_letter) in red_x_drum_blueprint.floor:
                checks = self.ungauged_code.borders[anchor][(
                    edge_colour, edge_letter)]
                floor.extend((t, check) for check in checks)
            for (t, edge_colour, edge_letter) in red_x_drum_blueprint.lid:
                checks = self.ungauged_code.borders[anchor][(
                    edge_colour, edge_letter)]
                lid.extend((t, check) for check in checks)
            drum_anchor = embed_coords(anchor, 3)
            detectors.append(Drum(floor, lid, 0, drum_anchor))
        self.final_detector_schedule[1].extend(detectors)

        data_qubits = self.data_qubits.values()
        final_measurements = [Pauli(qubit, PauliLetter("X"))
                              for qubit in data_qubits]
        qubit_check_dic = dict()
        final_checks = []
        for pauli in final_measurements:
            check = Check([pauli], pauli.qubit.coords)
            final_checks.append(check)
            qubit_check_dic[pauli.qubit] = check
        self.final_check_schedule = [
            self.ungauged_code.check_schedule[0], self.ungauged_code.check_schedule[2], final_checks]

        # add the small detectors at the end!
        final_detectors = []
        for check in (self.final_check_schedule[-2]):
            qubits = list(check.paulis.values())
            check_lid_0 = qubit_check_dic[qubits[0].qubit]
            check_lid_1 = qubit_check_dic[qubits[1].qubit]

            final_detectors.append(
                Drum([(-1, check)], [(0, check_lid_0), (0, check_lid_1)], 2))

        for check in (self.final_check_schedule[-3]):
            qubits = list(check.paulis.values())
            check_lid_0 = qubit_check_dic[qubits[0].qubit]
            check_lid_1 = qubit_check_dic[qubits[1].qubit]

            final_detectors.append(
                Drum([(-2, check)], [(0, check_lid_0), (0, check_lid_1)], 2))

        self.final_detector_schedule[2].extend(final_detectors)

    def get_ungauged_code(self, distance: int) -> TicTacToeCode:
        return FloquetColourCode(distance)

    def get_plaquette_detector_schedule(self) -> List[List[Drum]]:
        # Rather than build the actual detectors from scratch, build the
        # blueprints, and let the ungauged code build the actual detectors.

        # Start with X detectors
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

        # Now do Z detectors
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

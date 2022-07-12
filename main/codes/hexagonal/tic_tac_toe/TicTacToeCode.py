from collections import defaultdict
from typing import List, Tuple

from main.Colour import Colour, Red, Blue, Green
from main.building_blocks.Check import Check
from main.building_blocks.Detector import Detector
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.FloquetCode import FloquetCode
from main.codes.hexagonal.ToricHexagonalCode import ToricHexagonalCode
from main.codes.hexagonal.tic_tac_toe.DetectorBlueprint import DetectorBlueprint
from main.utils.utils import mid, xor

TicTacToeRoute = List[Tuple[Colour, PauliLetter]]


class TicTacToeCode(ToricHexagonalCode, FloquetCode):
    def __init__(self, distance: int, tic_tac_toe_route: TicTacToeRoute):
        # Initialise parent class immediately so that we have data qubits
        # etc available for use in the rest of this init.
        super().__init__(distance)

        assert self.follows_tic_tac_toe_rules(tic_tac_toe_route)
        assert self.is_good_code(tic_tac_toe_route)
        self.tic_tac_toe_route = tic_tac_toe_route

        checks, borders = self.create_checks()
        self.checks_by_type = checks
        stabilizers, relearned = self.find_stabilized_plaquettes()
        detector_blueprints = self.plan_detectors(stabilizers, relearned)
        detector_schedule = self.create_detectors(detector_blueprints, borders)

        check_schedule = [
            checks[(colour, pauli_letter)]
            for colour, pauli_letter in tic_tac_toe_route]

        self.set_schedules(check_schedule, detector_schedule)
        self.logical_qubits = self.get_init_logical_qubits()

        # Save some of the variables used above so that we can reference
        # them in tests. TODO - yuck!
        self.borders = borders
        self.stabilizers = stabilizers
        self.relearned = relearned
        self.detector_blueprints = detector_blueprints

    @staticmethod
    def follows_tic_tac_toe_rules(tic_tac_toe_route):
        """Tic-tac-toe rules state that the type of edges measured at each
        timestep must differ in column and row from those measured at the
        previous timestep.
        """
        length = len(tic_tac_toe_route)
        valid = length > 0
        if valid:
            this_colour, this_letter = tic_tac_toe_route[0]
        else:
            this_colour, this_letter = (None, None)
        i = 0
        while valid and i < length:
            next_colour, next_letter = tic_tac_toe_route[(i + 1) % length]
            valid = this_colour != next_colour and this_letter != next_letter
            this_colour = next_colour
            this_letter = next_letter
            i += 1
        return valid

    @staticmethod
    def is_good_code(tic_tac_toe_route):
        """This method assumes code follows tic tac toe rules already.
        Once a tic-tac-toe code has seven of the nine plaquette types in its
        stabilizer group, it will always have seven, regardless of which
        cell of the grid we choose at each future timestep. A code is 'good'
        if it reaches this point as quickly as possible. The minimum is four
        timesteps, and occurs if and only if we choose a 'cycle' of four
        colours in the first four steps, e.g. RGBR, GRBG, etc.
        """
        start = [colour for colour, _ in tic_tac_toe_route[:4]]
        first_three_colours_differ = len(set(start[:3])) == 3
        length = len(tic_tac_toe_route)
        start_colours_form_cycle = start[0] == start[3 % length]
        return first_three_colours_differ and start_colours_form_cycle

    def create_checks(self):
        # Idea: a plaquette of colour colours[i] is responsible for creating
        # any checks of colour colours[i+1] around its border. If this is
        # repeated across all plaquettes, we will create exactly all the
        # checks in the code.

        # Keep track of which checks form borders of which plaquettes.
        # This will be necessary when defining the detectors of the code
        # (the checks we want to multiply together to detect errors).
        borders = defaultdict(lambda: defaultdict(list))

        # Some edge types (squares of the tic-tac-tie grid) may not be used -
        # quickly note down which ones are used.
        edge_types_used = {colour: set() for colour in self.colours}
        for (colour, pauli_letter) in self.tic_tac_toe_route:
            edge_types_used[colour].add(pauli_letter)

        checks = defaultdict(list)
        # Start by iterating over all the red plaquettes, then green, etc.
        for i in range(3):
            plaquette_colour = self.colours[i]
            edge_colour = self.colours[(i+1) % 3]
            # Only do anything with plaquettes of this colour (colours[i])
            # if checks of next colour (colours[i+1]) are actually used.
            pauli_letters = edge_types_used[edge_colour]
            if len(pauli_letters) > 0:
                # Loop through all plaquettes of colour colours[i]
                anchors = self.colourful_plaquette_anchors[plaquette_colour]
                for anchor in anchors:
                    self.add_checks_around_plaquette(
                        anchor, edge_colour, pauli_letters, checks, borders)

        return checks, borders

    def add_checks_around_plaquette(
            self, anchor, edge_colour, pauli_letters, checks, borders):
        """Add checks of one colour around the border of a single plaquette.
        """
        corners = self.get_neighbours(anchor)
        for j in range(3):
            u, v = corners[2 * j], corners[2 * j + 1]
            midpoint = mid(u, v)
            # The edge (u, v) is a colours[i+1]-check, shared
            # between this plaquette of colour colours[i] and a
            # neighbouring one of colour colours[i+2]. The
            # neighbouring plaquette has its anchor along the line
            # between this plaquette's anchor and mid(u,v).
            diff = (midpoint[0] - anchor[0], midpoint[1] - anchor[1])
            neighbour_anchor = self.wrap_coords(
                (midpoint[0] + diff[0], midpoint[1] + diff[1]))
            qubit_u = self.data_qubits[self.wrap_coords(u)]
            qubit_v = self.data_qubits[self.wrap_coords(v)]

            for letter in pauli_letters:
                # Create the check object and note which plaquettes it borders
                paulis = [Pauli(qubit_u, letter), Pauli(qubit_v, letter)]
                check = Check(paulis, anchor=midpoint, colour=edge_colour)
                checks[(edge_colour, letter)].append(check)
                borders[anchor][(edge_colour, letter)].append(check)
                borders[neighbour_anchor][(edge_colour, letter)].append(check)

    def find_stabilized_plaquettes(self):
        # Track which plaquettes are stabilized, at what times, and which
        # edge measurements most recently stabilized them.
        stabilized = defaultdict(lambda: defaultdict(list))
        relearned = defaultdict(lambda: defaultdict(bool))

        length = len(self.tic_tac_toe_route)
        # We checked that this code is 'good', so after the first 4 steps,
        # the stabilizer pattern repeats every `length` steps. Thus we only
        # need to know what happens in the first 4 + length steps to know
        # the stabilizer patterns for all timesteps.
        repeats_after = length + 4
        for t in range(repeats_after):
            edge_colour, edge_letter = self.tic_tac_toe_route[t % length]
            # Picture tic-tac-toe grid: let (edge_colour, edge_letter) be the
            # 'current element' of the grid.
            
            # (Re)learn the rest of the 'row' of plaquettes
            relearned_plaquettes = self.relearn_plaquettes(
                t, stabilized, relearned, edge_colour, edge_letter)
            # Kick out anti-commuting plaquettes in the rest of the 'column'
            removed_plaquettes = self.remove_plaquettes(
                t, stabilized, edge_colour, edge_letter)

            if t > 0:
                # All other types of plaquettes remain in the stabilizer group,
                # if they were there before.
                self.carry_over_plaquettes(
                    t, stabilized, edge_colour, edge_letter)

                # Perhaps we can (re)infer some other plaquettes from the new
                # edge measurements.
                self.reinfer_plaquettes(
                    t, stabilized, relearned, relearned_plaquettes,
                    removed_plaquettes)

        return stabilized, relearned

    def reinfer_plaquettes(
            self, t, stabilized, relearned, relearned_plaquettes,
            anti_commuting_plaquettes):
        # There are only four candidate squares of the grid that we might
        # be able to (re)infer: those in the same columns as the (re)learned
        # plaquettes and same rows as the removed plaquettes.
        [l1, l2] = [letter for _, letter in anti_commuting_plaquettes]

        def reinfer_letter_plaquettes(l_a, l_b, l_c, colour):
            existing = stabilized[t][(colour, l_b)]
            if stabilized[t][(colour, l_a)]:
                # Can potentially infer stabilizers again - first check this
                # new information is more current than existing information.
                # No canonical mathematical definition of 'more current' - can
                # choose own. Better way of doing this stuff is in terms of
                # 'independent' detectors, but that's harder to code.
                # This should suffice for our needs.
                inferred = [
                    edge_type
                    for l in [l_a, l_c]
                    for edge_type in stabilized[t][(colour, l)]]
                min_existing = min([u for u, _, _ in existing], default=-1)
                min_inferred = min([u for u, _, _ in inferred])
                if min_inferred > min_existing:
                    # Can (re)infer plaquettes of type (colour, l_b)
                    relearned[t][(colour, l_b)] = True
                else:
                    # Leave it as it was - if we were to infer a stabilizer
                    # here it would at least in part be based on older
                    # information than the existing info we have.
                    inferred = existing
            else:
                # Leave (colour, l_b) as it was.
                inferred = existing
            return inferred

        for colour, l3 in relearned_plaquettes:
            inferred_l2 = reinfer_letter_plaquettes(l1, l2, l3, colour)
            inferred_l1 = reinfer_letter_plaquettes(l2, l1, l3, colour)
            stabilized[t][(colour, l1)] = inferred_l1
            stabilized[t][(colour, l2)] = inferred_l2

    def carry_over_plaquettes(self, t, stabilized, edge_colour, edge_letter):
        unaffected_plaquettes = [
            (colour, letter)
            for colour in self.colours for letter in self.letters
            if not xor(colour == edge_colour, letter == edge_letter)]
        for colour, letter in unaffected_plaquettes:
            stabilized[t][(colour, letter)] = \
                stabilized[t - 1][(colour, letter)]

    def remove_plaquettes(self, t, stabilized, edge_colour, edge_letter):
        anti_commuting_plaquettes = \
            self.rest_of_column(edge_colour, edge_letter)
        for colour, letter in anti_commuting_plaquettes:
            stabilized[t][(colour, letter)] = []
        return anti_commuting_plaquettes

    def relearn_plaquettes(self, t, stabilized, relearned, edge_colour, edge_letter):
        relearned_plaquettes = self.rest_of_row(edge_colour, edge_letter)
        for colour, letter in relearned_plaquettes:
            edge_type = (t, edge_colour, edge_letter)
            stabilized[t][(colour, letter)] = [edge_type]
            relearned[t][(colour, letter)] = True
        return relearned_plaquettes

    def plan_detectors(self, stabilizers, relearned):
        detector_blueprints = defaultdict(list)

        for colour in self.colours:
            for letter in self.letters:
                blueprints = self.plan_detectors_of_type(
                    colour, letter, stabilizers, relearned)
                for blueprint in blueprints:
                    # For a given colour, it's possible that different
                    # detectors in fact just compare the same set of checks,
                    # so we only want to take 'unique' ones.
                    # TODO - do we!?!?! What happens if we duplicate them!?
                    #  Would be lovely if Stim already handles it...
                    # unique = not any(
                    #     x.equivalent_to(blueprint)
                    #     for x in detector_blueprints[colour])
                    # if unique:
                    #     detector_blueprints[colour].append(blueprint)
                    detector_blueprints[colour].append(blueprint)

        return detector_blueprints

    def time_within_repeating_part_of_code(self, time: int):
        """Since we assumed this code is 'good', after 4 timesteps it repeats
        every `length` timesteps. So we can learn everything about the code
        by looking in the interval [4, length+4). This method returns the
        corresponding timestep in (or 'modulo') this interval. So e.g.
            0 -> length
            1 -> length + 1
            ...
            3 -> length + 3
            4 -> 4
            5 -> 5
            ...
            length + 3 -> length + 3
            length + 4 -> 4
            length + 5 -> 5
        """
        length = len(self.tic_tac_toe_route)
        return ((length - 4 + time) % length) + 4

    def plan_detectors_of_type(self, colour, letter, stabilizers, relearned):
        detector_blueprints = []
        length = len(self.tic_tac_toe_route)
        # Make a note of the first potential detector we find. Since the code
        # repeats, this helps us to know when to stop searching for detectors.
        first_detector_start = None
        # Track the 'floor' of the detector we're trying to build
        floor = None
        t = 0
        stop = length + 1
        while t < stop:
            u = self.time_within_repeating_part_of_code(t)
            # Find which edges (if any) most recently stabilized this type
            # of plaquette.
            stabilizing_edges = stabilizers[u][(colour, letter)]
            if len(stabilizing_edges) == 0:
                # This plaquette type has been destabilized, so any
                # detector we were thinking about building must be
                # abandoned.
                floor = None
            elif relearned[u][(colour, letter)]:
                # We've relearned this stabilizer, so we can try to
                # build a detector here.
                if first_detector_start is None:
                    # We will perform this search for another
                    # 'length' timesteps from now.
                    first_detector_start = t
                    stop += first_detector_start
                # Note down the 'actual' times t+v-u that the edges in this
                # detector face are measured, (rather than time within the
                # repeating part of the code).
                detector_face = [
                    ((t + v - u), c, l)
                    for v, c, l in stabilizing_edges]
                if floor is None:
                    # This is the 'bottom' of a potential detector cell
                    floor = detector_face
                else:
                    # This is the 'lid' of a detector cell and the
                    # 'bottom' of a potential next detector cell.
                    lid = detector_face
                    blueprint = DetectorBlueprint(length, t, floor, lid)
                    detector_blueprints.append(blueprint)
                    floor = detector_face
            t += 1

        return detector_blueprints

    def create_detectors(self, detector_blueprints, borders):
        detectors: List[List[Detector]] = [[] for _ in self.tic_tac_toe_route]
        # Loop through all red plaquettes, then green, then blue.
        for colour in self.colours:
            anchors = self.colourful_plaquette_anchors[colour]
            for anchor in anchors:
                for blueprint in detector_blueprints[colour]:
                    # Create an actual detector object from each blueprint.
                    floor, lid = [], []
                    for (t, edge_colour, edge_letter) in blueprint.floor:
                        checks = borders[anchor][(edge_colour, edge_letter)]
                        floor.extend((t, check) for check in checks)
                    for (t, edge_colour, edge_letter) in blueprint.lid:
                        checks = borders[anchor][(edge_colour, edge_letter)]
                        lid.extend((t, check) for check in checks)
                    detector = Detector(floor, lid, blueprint.learned)
                    detectors[blueprint.learned].append(detector)

        return detectors

    def get_logical_qubit_types(self, round: int):
        # 'round' is the round we've just finished doing measurements for.
        # The types returned will be the types of the operators immediately
        # after round 'round' up until right before round 'round + 1'.
        relative_round = round % len(self.tic_tac_toe_route)
        (prev_colour, prev_letter) = self.tic_tac_toe_route[relative_round]
        prev_row = self.rest_of_row(prev_colour, prev_letter)
        prev_column = self.rest_of_column(prev_colour, prev_letter)

        next_round = (relative_round + 1) % len(self.tic_tac_toe_route)
        (next_colour, next_letter) = self.tic_tac_toe_route[next_round]
        next_row = self.rest_of_row(next_colour, next_letter)
        next_column = self.rest_of_column(next_colour, next_letter)

        row_column_intersection = \
            set(prev_row).intersection(next_column).pop()
        column_row_intersection = \
            set(prev_column).intersection(next_row).pop()

        if round % 2 == 0:
            x_type = row_column_intersection
            z_type = column_row_intersection
        else:
            x_type = column_row_intersection
            z_type = row_column_intersection

        # Both X operators have the same type, likewise both Z operators.
        return x_type, z_type

    def get_init_logical_qubits(self):
        x_type, z_type = self.get_logical_qubit_types(-1)

        # Choose convention that the X operator is horizontal on qubit 0 but
        # vertical on qubit 1, and vice verse for Z operator.
        logical_0 = LogicalQubit(
            self.get_initial_horizontal_operator(x_type),
            self.get_initial_vertical_operator(z_type))
        logical_1 = LogicalQubit(
            self.get_initial_vertical_operator(x_type),
            self.get_initial_horizontal_operator(z_type))

        return [logical_0, logical_1]

    def get_initial_horizontal_operator(self, tic_tac_toe_square):
        # Logical 0's X operator and logical 1's Z operator are horizontal.
        colour, letter = tic_tac_toe_square
        starts = {
            Red: (8, 2),
            Blue: (2, 4),
            Green: (8, 6)}
        start = starts[colour]
        paulis = []
        for i in range(self.distance // 2):
            u = (start[0] + 12*i, start[1])
            v = (u[0] + 4, u[1])
            qubit_u = self.data_qubits[self.wrap_coords(u)]
            qubit_v = self.data_qubits[self.wrap_coords(v)]
            pauli_u = Pauli(qubit_u, letter)
            pauli_v = Pauli(qubit_v, letter)
            paulis.extend([pauli_u, pauli_v])
        return LogicalOperator(paulis)

    def get_initial_vertical_operator(self, tic_tac_toe_square):
        # Logical 0's Z operator and logical 1's X operator are vertical.
        colour, letter = tic_tac_toe_square
        starts = {
            Red: (6, 4),
            Blue: (6, 0),
            Green: (6, 8)}
        start = starts[colour]
        paulis = []
        for i in range(self.distance // 2):
            u = (start[0] + (i % 2) * 2, start[1] + 6 * i)
            v = (start[0] + 2 - (i % 2) * 2, start[1] + 2 + 6 * i)
            qubit_u = self.data_qubits[self.wrap_coords(u)]
            qubit_v = self.data_qubits[self.wrap_coords(v)]
            pauli_u = Pauli(qubit_u, letter)
            pauli_v = Pauli(qubit_v, letter)
            paulis.extend([pauli_u, pauli_v])
        return LogicalOperator(paulis)

    def rest_of_row(self, colour: Colour, letter: PauliLetter):
        return [
            (c, letter)
            for c in self.colours
            if c != colour]

    def rest_of_column(self, colour: Colour, letter: PauliLetter):
        return [
            (colour, l)
            for l in self.letters
            if l != letter]

    def update_logical_qubits(self, round: int):
        # 'round' is the round we've just finished doing measurements for.
        relative_round = round % self.schedule_length
        update_checks = defaultdict(list)

        # Mustn't use relative round in the following
        prev_x_type, prev_z_type = self.get_logical_qubit_types(round - 1)
        next_x_type, next_z_type = self.get_logical_qubit_types(round)

        if next_x_type != prev_x_type:
            # Need to update the logical X operators
            logical = self.logical_qubits[0].x
            update_checks[logical] = self.update_operator(
                logical, relative_round, vertical=False)
            logical = self.logical_qubits[1].x
            update_checks[logical] = self.update_operator(
                logical, relative_round, vertical=True)

        if next_z_type != prev_z_type:
            # Need to update the logical Z operators
            logical = self.logical_qubits[0].z
            update_checks[logical] = self.update_operator(
                logical, relative_round, vertical=True)
            logical = self.logical_qubits[1].z
            update_checks[logical] = self.update_operator(
                logical, relative_round, vertical=False)

        # Return - for each operator - the checks that have been multiplied
        # into this operator in order to update it.
        return update_checks

    def update_operator(
            self, operator: LogicalOperator, relative_round: int,
            vertical: bool = False):
        # Slightly different depending on whether operator is vertical or
        # horizontal - horizontal operators are multiplied by ALL
        # intersecting checks, whereas vertical ones are only multiplied by
        # those in their support (i.e. not horizontal ones).

        def intersect(check, operator):
            check_qubits = {pauli.qubit for pauli in check.paulis}
            operator_qubits = {pauli.qubit for pauli in operator.paulis}
            return len(check_qubits.intersection(operator_qubits)) > 0

        def is_horizontal(check):
            y_coords = [pauli.qubit.coords[1] for pauli in check.paulis]
            return len(set(y_coords)) == 1

        check_type = self.tic_tac_toe_route[relative_round]
        checks = self.checks_by_type[check_type]
        intersecting_checks = [
            check for check in checks
            if intersect(check, operator)]
        if vertical:
            intersecting_checks = [
                check for check in intersecting_checks
                if not is_horizontal(check)]
        intersecting_paulis = [
            pauli
            for check in intersecting_checks
            for pauli in check.paulis]

        operator.update(intersecting_paulis)
        return intersecting_checks

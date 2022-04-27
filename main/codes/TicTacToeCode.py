from collections import defaultdict
from typing import List, Tuple

from main.Colour import Colour, Red, Green, Blue
from main.building_blocks.Check import Check
from main.building_blocks.Operator import Operator
from main.building_blocks.Pauli import Pauli
from main.codes.FloquetCode import FloquetCode
from main.codes.ToricHexagonalCode import ToricHexagonalCode
from main.utils import mid


class TicTacToeCode(ToricHexagonalCode, FloquetCode):
    def __init__(self, distance: int,
                 tic_tac_toe: List[Tuple[Colour, Pauli]]):
        super().__init__(distance)

        checks = defaultdict(list)
        edge_types_used = {
            Red: set(),
            Green: set(),
            Blue: set()}
        for (colour, pauli) in tic_tac_toe:
            edge_types_used[colour].add(pauli)

        # Create all the required weight-two edge checks.
        for center, colour in self.colourful_plaquette_centers():
            # Only do anything with this plaquette if this colour is used in
            # the schedule.
            paulis = edge_types_used[colour]
            if len(paulis) > 0:
                # For each plaquette, we'll create the edges of that colour
                # that point outwards from it. But to create all edges, we
                # actually only need to look at every other edge leaving
                # this plaquette - the 'missing' ones will be filled in by
                # other plaquettes of this colour.
                every_other_neighbour = self.get_neighbours(center)[::2]
                for u in every_other_neighbour:
                    diff = (u[0] - center[0], u[1] - center[1])
                    v = (u[0] + diff[0], u[1] + diff[1])
                    mid_point = self.wrap_coords(mid(u, v))
                    u = self.data_qubits[self.wrap_coords(u)]
                    v = self.data_qubits[self.wrap_coords(v)]

                    for pauli in paulis:
                        ops = [Operator(u, pauli), Operator(v, pauli)]
                        check = Check(ops, mid_point, colour=colour)
                        checks[(colour, pauli)].append(check)

        schedule = [checks[(colour, pauli)] for colour, pauli in tic_tac_toe]
        self.set_schedule(schedule)









from typing import List

from main.utils.Colour import Blue, Green, Red
from main.building_blocks.Check import Check
from main.building_blocks.detectors.Stabilizer import Stabilizer
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.ToricHexagonalCode import ToricHexagonalCode
from main.utils.types import Coordinates
from main.utils.utils import coords_minus


class ToricXyzSquaredCode(ToricHexagonalCode):
    def __init__(self, distance_x: int, distance_z: int):
        assert distance_z % 2 == 0
        distance = min([distance_z, distance_x])
        assert distance > 1

        self.distance_x = distance_x
        self.distance_z = distance_z
        self.xyzxyz = [PauliLetter('X'), PauliLetter('Y'), PauliLetter('Z'), PauliLetter('X'), PauliLetter('Y'), PauliLetter('Z')]

        # Call super now so that we have data qubits available to us in a sec
        super().__init__(
            rows=distance_x,
            columns=distance_z,
            distance=distance)

        checks = self.create_checks()
        self.set_schedules([checks])
        self.logical_qubits = self.create_logical_qubits()

    def create_checks(self):
        checks = []
        for anchor in self.plaquette_anchors:
            corners = self.get_neighbour_coords(anchor)
            xyzxyz_check = self.create_xyzxyz_check(anchor, corners)
            xx_check = self.create_xx_check(corners[0])
            checks.extend([xyzxyz_check, xx_check])
        return checks

    def create_xx_check(self, left: Coordinates):
        # Create the XX check attached to the rightmost point of this face
        right = self.get_neighbour_coords(left)[0]
        X_left = Pauli(self.data_qubits[self.wrap_coords(left)], PauliLetter('X'))
        X_right = Pauli(self.data_qubits[self.wrap_coords(right)], PauliLetter('X'))
        midpoint = self.wrap_coords((left[0] + 2, left[1]))
        check = Check({(-2, 0): X_left, (2, 0): X_right}, midpoint, Blue)
        return check

    def create_xyzxyz_check(
            self, anchor: Coordinates, corners: List[Coordinates]):
        data_qubits = [
            self.data_qubits[self.wrap_coords(corner)]
            for corner in corners]
        offsets = [coords_minus(corner, anchor) for corner in corners]
        zipped = zip(offsets, data_qubits, self.xyzxyz)
        paulis = {
            offset: Pauli(qubit, letter)
            for offset, qubit, letter in zipped}
        colour = Green if self.is_electric_anchor(anchor) else Red
        check = Check(paulis, anchor, colour)
        return check

    def create_logical_qubits(self):
        # TODO - add the other three logical operators.
        support = [(8, 4 * i + 2) for i in range(self.distance_x)]
        paulis = [Pauli(self.data_qubits[coords], PauliLetter('X')) for coords in support]
        logical_x = LogicalOperator(paulis)
        logical_qubit = LogicalQubit(x=logical_x)
        return [logical_qubit]

    def get_plus_plus_stabilizers(self):
        # TODO - find and give the stabilizers for logical |00> ?
        initial_stabilizers = []
        final_stabilizers = []

        # First get the more complicated electric stabilizers
        for x in range(4, 12 * self.distance_z // 2, 12):
            for y in range(0, 4 * self.distance_x, 4):
                xx_anchor = (x, y)
                initial_stabilizer, final_stabilizer = \
                    self.get_plus_plus_electric_stabilizers(xx_anchor)
                initial_stabilizers.append(initial_stabilizer)
                final_stabilizers.append(final_stabilizer)

        # Now do the magnetic XX stabilizers
        for x in range(10, 12 * self.distance_z // 2, 12):
            for y in range(2, 4 * self.distance_x, 4):
                xx_check = next(
                    check for check in self.checks
                    if check.anchor == (x, y))
                initial_stabilizer = Stabilizer([(0, xx_check)], 0, (x, y, 0))
                initial_stabilizers.append(initial_stabilizer)
                final_stabilizer = Stabilizer([(-1, xx_check)], 0, (x, y, 0))
                final_stabilizers.append(final_stabilizer)

        return initial_stabilizers, final_stabilizers

    def get_plus_plus_electric_stabilizers(self, xx_anchor: Coordinates):
        # Take each electric XX check...
        x, y = xx_anchor
        xx_check = next(
            check for check in self.checks
            if check.anchor == xx_anchor)
        # ... and the electric XYZXYZ check above it...
        xyzxyz_check = next(
            check for check in self.checks if
            check.anchor == (x, y + 2))
        # ... and combine them into stabilizers.
        timed_checks = [(0, xx_check), (0, xyzxyz_check)]
        initial_stabilizer = Stabilizer(timed_checks, 0, (x, y + 2, 0))

        timed_checks = [(-1, xx_check), (-1, xyzxyz_check)]
        final_stabilizer = Stabilizer(timed_checks, 0, (x, y + 2, 0))

        return initial_stabilizer, final_stabilizer

    def is_electric_anchor(self, anchor: Coordinates):
        # Only applicable to weight-6 checks.
        # Might be a check anchor (2D coords) or might be a detector anchor
        # (3D coords) - only the first two coordinates are relevant.
        anchor = list(anchor)[:2]
        return anchor[0] % 12 == 4 and anchor[1] % 4 == 2

    def is_magnetic_anchor(self, anchor: Coordinates):
        # Only applicable to weight-6 checks.
        # Might be a check anchor (2D coords) or might be a detector anchor
        # (3D coords) - only the first two coordinates are relevant.
        anchor = list(anchor)[:2]
        return anchor[0] % 12 == 10 and anchor[1] % 4 == 0

    def is_xx_anchor(self, anchor: Coordinates):
        # Might be a check anchor (2D coords) or might be a detector anchor
        # (3D coords) - only the first two coordinates are relevant.
        anchor = list(anchor)[:2]
        return sum(anchor) % 4 == 0
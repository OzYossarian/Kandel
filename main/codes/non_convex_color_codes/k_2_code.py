
from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.building_blocks.logical.LogicalQubit import LogicalQubit
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.Code import Code
from main.codes.HexagonalCode import HexagonalCode
from main.codes.non_convex_color_codes.utils import *


class K2ColorCode(Code):
    """Non convex color code encoding two logical qubits

    Not using HexagonalCode because I'm not using a coordinates system with three coordinates.
    """

    def __init__(self, distance: int):

        self.data_qubits, self.ancilla_qubits = self.create_data_and_ancilla_qubits()
        checks = self.create_checks()
        logical_qubits = self.init_logical_qubits()
        # todo self init logical qubits
        super().__init__(
            data_qubits=self.data_qubits,
            check_schedule=[checks],
            distance=distance,
            logical_qubits=logical_qubits
        )

    def create_data_and_ancilla_qubits(self):
        triangular_lattice_vertexes = set()
        triangular_lattice_vertexes.update(
            generate_triangular_lattice(1, (1, 1, 1)))
        triangular_lattice_vertexes.update(
            generate_triangular_lattice(1, (1, -1, 3), True))

        data_qubits = {}
        ancilla_qubits = {}

        for q_coords in triangular_lattice_vertexes:
            if (q_coords[2] - q_coords[1]) % 3 != 2:
                data_qubits[q_coords] = Qubit(q_coords)

            else:
                ancilla_qubits[q_coords] = Qubit(q_coords)

        return (data_qubits, ancilla_qubits)

    def create_checks(self):
        translations = [(0, -1, 1), (1, 0, 1), (-1, 1, 0),
                        (0, 1, -1), (1, 0, -1), (1, -1, 0)]
        checks = []
        for anchor in self.ancilla_qubits:
            paulis_X = dict()
            paulis_Z = dict()
            for translation in translations:
                data_qubit_coords = (
                    anchor[0]+translation[0], anchor[1]+translation[1], anchor[2] + translation[2])
                if data_qubit_coords in self.data_qubits:
                    paulis_X[translation] = Pauli(
                        self.data_qubits[data_qubit_coords], PauliLetter('X'))
                    paulis_Z[translation] = Pauli(
                        self.data_qubits[data_qubit_coords], PauliLetter('Z'))

            checks.extend([Check(paulis_X, anchor), Check(paulis_Z, anchor)])

        return (checks)

    def init_logical_qubits(self):
        # logical qubit 1 has qubits defined on the bottom_row
        # logical qubit 2 has qubits defined on the top_row
        bottom_row_cords = [(3, 0, 0), (1, 2, 0), (0, 3, 0)]
        lx_1 = LogicalOperator(
            [Pauli(self.data_qubits[coords], PauliLetter("X")) for coords in bottom_row_cords])
        lz_1 = LogicalOperator(
            [Pauli(self.data_qubits[coords], PauliLetter("Z")) for coords in bottom_row_cords])
        lq_1 = LogicalQubit(x=lx_1, z=lz_1)

        top_row_cords = [(2, -3, 4), (1, -2, -4), (-1, 0, 4)]
        lx_2 = LogicalOperator(
            [Pauli(self.data_qubits[coords], PauliLetter("X")) for coords in bottom_row_cords])
        lz_2 = LogicalOperator(
            [Pauli(self.data_qubits[coords], PauliLetter("Z")) for coords in bottom_row_cords])
        lq_2 = LogicalQubit(x=lx_2, z=lz_2)
        return ([lq_1, lq_2])

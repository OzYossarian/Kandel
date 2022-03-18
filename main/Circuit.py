import stim
from main.building_blocks.Qubit import Qubit
from main.building_blocks.Pauli import PauliX, PauliZ, PauliY
from main.building_blocks.Check import Check
from main.enums import State


class Circuit():
    def __init__(self):
        self.initialized_qubit_coordinates = set()
        self.stim_circuit = stim.Circuit()
        self.coord_to_stim_index = dict()

    def initialize_qubits(self, qubits: [Qubit]):
        for qubit in qubits:
            # add that a new timestep needs to be created if there's overlap
            if qubit.coords not in self.initialized_qubit_coordinates:
                if qubit.initial_state == State(0):
                    self.stim_circuit.append_operation(
                        "RZ", len(self.coord_to_stim_index.keys()))
                self.initialized_qubit_coordinates.add(qubit.coords)
                if qubit.coords != self.coord_to_stim_index.keys():
                    self.coord_to_stim_index[qubit.coords] = len(
                        self.coord_to_stim_index.keys())

    def check_to_stim_cnot(self, check: Check):

        for operator in check.operators:
            if operator.pauli == PauliZ:
                self.stim_circuit.append_operation(
                    "CNOT", [self.coord_to_stim_index[operator.qubit.coords], self.coord_to_stim_index[check.ancilla.coords]])

        #print(check, 'check')
        # pass
        # compile and add measurements

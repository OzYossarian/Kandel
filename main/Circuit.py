import stim
from main.building_blocks.Qubit import Qubit
from main.building_blocks.Pauli import Pauli, PauliX, PauliZ, PauliY
from main.building_blocks.Check import Check
from main.enums import State


class Circuit():
    def __init__(self):
        self.stim_circuit = stim.Circuit()
        self.coord_to_stim_index = dict()

    def to_stim(gates_at_timesteps):
        for timestep in gates_at_timesteps:
            for qubits, gates in gates_at_timesteps[timestep]['gates'].items:
                print(qubits, 'qubits')
                print(gates, 'gates')

    def check_to_stim_cnot(self, check: Check):

        for operator in check.operators:
            if operator.pauli == PauliZ:
                self.stim_circuit.append_operation(
                    "CNOT", [self.coord_to_stim_index[operator.qubit.coords], self.coord_to_stim_index[check.ancilla.coords]])

    def measure_qubits(self, qubits: [Qubit], basis: Pauli):
        for qubit in qubits:
            if basis == PauliZ:
                self.stim_circuit.append_operation(
                    'MRZ', self.coord_to_stim_index[qubit.coords])
            elif basis == PauliX:
                self.stim_circuit.append_operation(
                    'MRX', self.coord_to_stim_index[qubit.coords])
            elif basis == PauliY:
                self.stim_circuit.append_operation(
                    'MRY', self.coord_to_stim_index[qubit.coords])
            self.initialized_qubit_coordinates.remove(qubit.coords)

        # print(check, 'check')
        # pass
        # compile and add measurements

from typing import Tuple
from xml.dom.minidom import Element
import stim
from main.building_blocks.Qubit import Qubit
from main.building_blocks.Pauli import Pauli, PauliX, PauliZ, PauliY
from main.building_blocks.Check import Check
from main.enums import State


class Circuit():
    def __init__(self):
        self.stim_circuit = stim.Circuit()
        self.coord_to_stim_index = dict()
        self.measured_qubits = dict()

    def to_stim(self, gates_at_timesteps):
        for timestep in gates_at_timesteps:
            for qubits, gate in gates_at_timesteps[timestep]['gates'].items():
                if gate[0] == "M":
                    if type(qubits) == tuple:
                        self.translate_data_qubit_measurement_gates(
                            gate, qubits[0], qubits[1])
                    else:
                        self.translate_measurement_gates(
                            gate, qubits)

                elif type(qubits) == tuple:
                    self.translate_two_qubit_gate(gate, qubits)

                else:
                    self.translate_qubit_gate(gate, qubits)

            self.stim_circuit.append_operation("TICK")

    def translate_qubit_gate(self, gate: str, qubit: Qubit):
        if qubit.coords not in self.coord_to_stim_index.keys():
            self.coord_to_stim_index[qubit.coords] = len(
                self.coord_to_stim_index.keys())
        self.stim_circuit.append_operation(
            gate, self.coord_to_stim_index[qubit.coords])

    def translate_two_qubit_gate(self, gate: str, qubits: (Qubit)):
        stim_qubits = []
        for qubit in qubits:
            if qubit.coords not in self.coord_to_stim_index.keys():
                self.coord_to_stim_index[qubit.coords] = len(
                    self.coord_to_stim_index.keys())
            stim_qubits.append(self.coord_to_stim_index[qubit.coords])
        self.stim_circuit.append_operation(gate, stim_qubits)

    def translate_data_qubit_measurement_gates(self, measurement_gate: str,
                                               data_qubits: Tuple[Qubit],
                                               detector_qubits: Tuple[Qubit]):

        detector_list = []
        for index, data_qubit in enumerate(data_qubits):
            self.stim_circuit.append_operation(
                measurement_gate, self.coord_to_stim_index[data_qubit.coords])
            for measured_qubits in self.measured_qubits:
                self.measured_qubits[measured_qubits] -= 1
            detector_list.append(stim.target_rec(-index-1))
            self.measured_qubits[data_qubit] = -1

        for det_qubit in detector_qubits:
            detector_list.append(stim.target_rec(
                self.measured_qubits[det_qubit]))
        self.stim_circuit.append_operation("DETECTOR", (detector_list))

    def translate_measurement_gates(self, measurement_gate: str, qubit: Qubit,):
        if qubit.coords not in self.coord_to_stim_index.keys():
            self.coord_to_stim_index[qubit.coords] = len(
                self.coord_to_stim_index.keys())
        self.stim_circuit.append_operation(
            measurement_gate, self.coord_to_stim_index[qubit.coords])

        for measured_qubits in self.measured_qubits:
            self.measured_qubits[measured_qubits] -= 1
        if qubit in self.measured_qubits:
            self.stim_circuit.append_operation(
                "DETECTOR", [stim.target_rec(-1), stim.target_rec(self.measured_qubits[qubit])])
        else:
            self.stim_circuit.append_operation(
                "DETECTOR", [stim.target_rec(-1)])

        self.measured_qubits[qubit] = -1

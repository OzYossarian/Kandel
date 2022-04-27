from timeit import repeat
from typing import Tuple
from xml.dom.minidom import Element
import stim
from main.building_blocks.Qubit import Qubit
from main.building_blocks.Pauli import Pauli, PauliX, PauliZ, PauliY
from main.building_blocks.Check import Check
from main.enums import State


class Circuit():
    def __init__(self):
        self.full_circuit = stim.Circuit()
        self.coord_to_stim_index = dict()
        self.measured_qubits = dict()

    def to_stim(self, gates_at_timesteps, detector_qubits, n_code_rounds=1):
        before_repeat_block = True
        self.stim_circuit = stim.Circuit()
        for timestep in gates_at_timesteps:

            if gates_at_timesteps[timestep]['repeat'] == True and before_repeat_block == True:
                before_repeat_block = False
                self.full_circuit += self.stim_circuit
                self.stim_circuit = stim.Circuit()
            elif gates_at_timesteps[timestep]['repeat'] == False and before_repeat_block == False:
                before_repeat_block = True
                if n_code_rounds > 2:
                    repeat_block = stim.CircuitRepeatBlock(
                        n_code_rounds-2, self.stim_circuit)
                    self.full_circuit.append_operation(repeat_block)
                self.stim_circuit = stim.Circuit()

            for qubits, gate in gates_at_timesteps[timestep]['gates'].items():
                if gate[0] == "M":
                    if type(qubits) == tuple:
                        self.translate_data_qubit_measurement_gates(
                            gate, qubits[0], qubits[1], qubits[2], detector_qubits)
                    else:
                        self.translate_measurement_gates(
                            gate, qubits, detector_qubits)
                elif gate == "Observable":
                    self.add_observable(qubits)

                elif type(qubits) == tuple:
                    self.translate_two_qubit_gate(gate, qubits)

                else:
                    self.translate_qubit_gate(gate, qubits)

            self.translate_noise(gates_at_timesteps[timestep]['noise'])
            self.stim_circuit.append_operation("TICK")
        self.full_circuit += self.stim_circuit

    def translate_noise(self, noise_operations):
        for noise_target, noise in noise_operations.items():
            for noise_term in noise:

                # two qubit noise
                if type(noise_target) == tuple:
                    self.stim_circuit.append_operation(
                        noise_term[0], [self.coord_to_stim_index[
                            noise_target[0].coords],
                            self.coord_to_stim_index[noise_target[1].coords]],
                        noise_term[1])

                # single qubit noise
                else:
                    self.stim_circuit.append_operation(
                        noise_term[0], [self.coord_to_stim_index[noise_target.coords]], noise_term[1])

    def translate_qubit_gate(self, gate: str, qubit: Qubit):
        if qubit.coords not in self.coord_to_stim_index.keys():
            self.coord_to_stim_index[qubit.coords] = len(
                self.coord_to_stim_index.keys())
        self.stim_circuit.append_operation(
            gate, self.coord_to_stim_index[qubit.coords])

    def add_observable(self, qubits: (Qubit)):

        observable_list = []
        for qubit in qubits:
            observable_list.append(
                stim.target_rec(self.measured_qubits[qubit]))
        self.stim_circuit.append_operation(
            "OBSERVABLE_INCLUDE", (observable_list))

    def translate_two_qubit_gate(self, gate: str, qubits: (Qubit)):
        stim_qubits = []
        for qubit in qubits:
            if qubit.coords not in self.coord_to_stim_index.keys():
                self.coord_to_stim_index[qubit.coords] = len(
                    self.coord_to_stim_index.keys())
            stim_qubits.append(self.coord_to_stim_index[qubit.coords])
        self.stim_circuit.append_operation(gate, stim_qubits)

    def translate_data_qubit_measurement_gates(self, measurement_gate: str,
                                               data_qubits_to_measure: Tuple[Qubit],
                                               data_qubits_measured: Tuple[Qubit],
                                               ancilla_qubit: Qubit,
                                               detector_qubits: Tuple[Qubit]):

        detector_list = []
        for index, data_qubit in enumerate(data_qubits_to_measure):
            self.stim_circuit.append_operation(
                measurement_gate, self.coord_to_stim_index[data_qubit.coords])
            for measured_qubits in self.measured_qubits:
                self.measured_qubits[measured_qubits] -= 1
            detector_list.append(stim.target_rec(-index-1))
            self.measured_qubits[data_qubit] = -1

        if ancilla_qubit in detector_qubits:
            for data_qubit in data_qubits_measured:
                detector_list.append(stim.target_rec(
                    self.measured_qubits[data_qubit]))
            detector_list.append(stim.target_rec(
                self.measured_qubits[ancilla_qubit]))
            self.stim_circuit.append_operation("DETECTOR", (detector_list))

    def translate_measurement_gates(self, measurement_gate: str, qubit: Qubit,
                                    detector_qubits: set[Qubit] = None):
        if qubit.coords not in self.coord_to_stim_index.keys():
            self.coord_to_stim_index[qubit.coords] = len(
                self.coord_to_stim_index.keys())
        self.stim_circuit.append_operation(
            measurement_gate, self.coord_to_stim_index[qubit.coords])

        for measured_qubits in self.measured_qubits:
            self.measured_qubits[measured_qubits] -= 1
        if qubit in self.measured_qubits and qubit in detector_qubits:
            self.stim_circuit.append_operation(
                "DETECTOR", [stim.target_rec(-1), stim.target_rec(self.measured_qubits[qubit])])
        else:
            if qubit in detector_qubits:
                self.stim_circuit.append_operation(
                    "DETECTOR", [stim.target_rec(-1)])

        self.measured_qubits[qubit] = -1

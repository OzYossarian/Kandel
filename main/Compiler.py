from time import time
from main.NoiseModel import NoiseModel
from main.QPUs.QPU import QPU
from main.Circuit import Circuit
from main.codes.Code import Code
from main.building_blocks.Pauli import Pauli, PauliX, PauliZ, PauliY
from main.building_blocks.Qubit import Qubit
from main.building_blocks.Operator import Operator
from main.building_blocks.Check import Check
from main.enums import State
import copy


empty_timestep = {'occupied_qubits': set(),
                  'initialized_qubits': set(),
                  'gates': dict(),
                  'noise': dict()}


class Compiler(object):
    def __init__(self, noise_model=None):

        if noise_model == None:
            self.noise_model = NoiseModel()
        else:
            self.noise_model = noise_model

        self.gates_at_timesteps = dict()
        self.gates_at_timesteps[0] = copy.deepcopy(empty_timestep)

    def compile_qpu(self, qpu: QPU, circuit: Circuit, n_timesteps: int = 1):
        for code in qpu.codes:
            self.compile_code(code, circuit, n_timesteps)
        circuit.to_stim(self.gates_at_timesteps)

    def compile_code(self, code: Code, measure_data_qubits=False, n_code_rounds=1):

        self.initialize_qubits(code.data_qubits.values(), 0, 'data')
        initial_timestep = 0
        for _ in range(n_code_rounds):
            if self.noise_model.data_qubit_start_round != 0:
                self.add_noise_start_round_data_qubits(
                    code.data_qubits.values(), initial_timestep)

            for round in code.schedule:
                initial_timestep = self.compile_one_round(
                    round, initial_timestep)
            # add phenomenological noise at end of each round

        if measure_data_qubits == True:
            self.measure_data_qubits(code,
                                     PauliZ, timestep=initial_timestep-1)
            self.add_logical_observable(code.logical_operator,
                                        PauliZ, timestep=initial_timestep-1)

    def add_noise_start_round_data_qubits(self, data_qubits, timestep):
        if timestep not in self.gates_at_timesteps:
            self.gates_at_timesteps[timestep] = copy.deepcopy(empty_timestep)
            self.gates_at_timesteps[timestep]['initialized_qubits'] = copy.copy(
                self.gates_at_timesteps[timestep-1]['initialized_qubits'])
        for qubit in data_qubits:
            self.gates_at_timesteps[timestep]['noise'][qubit] = self.noise_model.data_qubit_start_round

    def compile_one_round(self, round: [Check], initial_timestep: int):
        for check in round:
            self.initialize_qubits(
                [check.ancilla], initial_timestep +
                check.initialization_timestep)

            for operator in check.operators:

                self.translate_operator(
                    operator, check.ancilla)

            measurement_timestep = len(check.operators) + \
                initial_timestep+check.initialization_timestep

            self.measure_ancilla_qubit(
                check.ancilla, measurement_timestep)

        return(len(self.gates_at_timesteps))

    def measure_ancilla_qubit(self, qubit: Qubit, timestep):
        timestep = self.find_timestep(qubit, timestep)

        if qubit.initial_state == State.Zero:
            self.gates_at_timesteps[timestep]['gates'][qubit] = 'MRZ'
            if self.noise_model.ancilla_qubit_MZ != 0:
                self.gates_at_timesteps[timestep -
                                        1]['noise'][qubit] = self.noise_model.ancilla_qubit_MZ

        elif qubit.initial_state == State.Plus:
            self.gates_at_timesteps[timestep]['gates'][qubit] = "H"
            self.gates_at_timesteps[timestep]['occupied_qubits'].add(
                qubit)
            if timestep+1 not in self.gates_at_timesteps:
                self.gates_at_timesteps[timestep +
                                        1] = copy.deepcopy(empty_timestep)
                self.gates_at_timesteps[timestep+1]['initialized_qubits'] = copy.copy(
                    self.gates_at_timesteps[timestep]['initialized_qubits'])

            self.gates_at_timesteps[timestep+1]['gates'][qubit] = 'RZ'

        for future_timestep in range(timestep, len(self.gates_at_timesteps)):
            self.gates_at_timesteps[future_timestep]['initialized_qubits'].remove(
                qubit)
        self.gates_at_timesteps[timestep]['occupied_qubits'].add(
            qubit)

    def measure_data_qubits(self,  code: Code, basis, timestep: int):
        """
        The code here is messy. This is because stim needs to know which
        ancilla measurement result should be the same as the data qubit
        measurement result
        """
        for check in code.schedule[0]:
            qubits_to_measure = tuple()
            qubits_for_detector = tuple()

            for operator in check.operators:
                if operator.qubit in self.gates_at_timesteps[timestep]['initialized_qubits']:

                    qubits_to_measure += (operator.qubit,)
                else:
                    qubits_for_detector += (operator.qubit,)
            qubits_for_detector += (check.ancilla,)
            qubits = (qubits_to_measure, qubits_for_detector)

            # add case where data qubits are already measured!
            if basis == PauliZ:
                self.gates_at_timesteps[timestep]['gates'][qubits] = 'MRZ'
            elif basis == PauliX:
                self.gates_at_timesteps[timestep]['gates'][qubits] = 'MRX'
            elif basis == PauliY:
                self.gates_at_timesteps[timestep]['gates'][qubits] = 'MRY'

            for qubit in qubits_to_measure:
                self.gates_at_timesteps[timestep]['occupied_qubits'].add(
                    qubit)

                for future_timestep in range(timestep, len(self.gates_at_timesteps)):
                    self.gates_at_timesteps[future_timestep]['initialized_qubits'].remove(
                        qubit)

    def add_logical_observable(self, logical_op: [Operator], basis: PauliZ, timestep: int):
        qubits = tuple()
        for operator in logical_op:
            qubits += (operator.qubit,)
        self.gates_at_timesteps[timestep]['gates'][qubits] = "Observable"

    def initialize_qubits(self, qubits: [Qubit], timestep: int, qubit_type='ancilla'):
        if timestep not in self.gates_at_timesteps:
            for i in range(2):
                self.gates_at_timesteps[timestep +
                                        i] = copy.deepcopy(empty_timestep)
                self.gates_at_timesteps[timestep+i]['initialized_qubits'] = copy.copy(
                    self.gates_at_timesteps[timestep-1+i]['initialized_qubits'])

        for qubit in qubits:
            if qubit not in self.gates_at_timesteps[timestep]['initialized_qubits']:
                if qubit.initial_state == State.Zero:
                    if qubit_type == 'data' and self.noise_model.data_qubit_RZ != 0:
                        self.gates_at_timesteps[timestep]['noise'][qubit] = self.noise_model.data_qubit_RZ
                    self.gates_at_timesteps[timestep]['gates'][qubit] = "RZ"
                    self.gates_at_timesteps[timestep]['occupied_qubits'].add(
                        qubit)
                elif qubit.initial_state == State.Plus:
                    self.gates_at_timesteps[timestep]['gates'][qubit] = "RZ"
                    self.gates_at_timesteps[timestep]['occupied_qubits'].add(
                        qubit)

                    self.gates_at_timesteps[timestep+1]['gates'][qubit] = "H"
                    self.gates_at_timesteps[timestep+1]['occupied_qubits'].add(
                        qubit)

                for future_timestep in range(timestep, len(self.gates_at_timesteps)):
                    self.gates_at_timesteps[future_timestep]['initialized_qubits'].add(
                        qubit)

    def translate_operator(self, operator: Operator, ancilla: Qubit):
        timestep_ancilla = self.find_timestep(ancilla)
        timestep_data_qubit = self.find_timestep(operator.qubit)
        timestep = max([timestep_ancilla, timestep_data_qubit])

        self.gates_at_timesteps[timestep]['occupied_qubits'].add(
            operator.qubit)
        self.gates_at_timesteps[timestep]['occupied_qubits'].add(
            ancilla)
        if operator.pauli == PauliZ:
            self.gates_at_timesteps[timestep]['gates'][operator.qubit,
                                                       ancilla] = "CNOT"
        if operator.pauli == PauliX:
            self.gates_at_timesteps[timestep]['gates'][ancilla,
                                                       operator.qubit] = "CNOT"

    def find_timestep(self, qubit: Qubit, start_timestep=0):
        for timestep in range(start_timestep, len(self.gates_at_timesteps.keys())):
            if qubit not in self.gates_at_timesteps[timestep]['occupied_qubits']:
                if qubit in self.gates_at_timesteps[timestep]['initialized_qubits']:
                    return(timestep)
        else:
            self.gates_at_timesteps[timestep+1] = copy.deepcopy(empty_timestep)
            self.gates_at_timesteps[timestep+1]['initialized_qubits'] = copy.copy(
                self.gates_at_timesteps[timestep]['initialized_qubits'])
            return(timestep+1)

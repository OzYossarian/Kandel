from time import time
from numpy import empty
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
                  'gates': dict()}


class Compiler(object):
    def __init__(self, noise_model=None):
        self.gates_at_timesteps = dict()
        self.gates_at_timesteps[0] = copy.deepcopy(empty_timestep)
        pass

    def compile_qpu(self, qpu: QPU, circuit: Circuit, n_timesteps: int = 1):
        for code in qpu.codes:
            self.compile_code(code, circuit, n_timesteps)
        circuit.to_stim(self.gates_at_timesteps)

    def compile_code(self, code: Code, measure_data_qubits=False, n_code_rounds=1):

        self.initialize_qubits(code.data_qubits.values(), 0)
        initial_timestep = 0
        for _ in range(n_code_rounds):
            for round in code.schedule:
                initial_timestep = self.compile_one_round(
                    round, initial_timestep)
        if measure_data_qubits == True:
            self.measure_qubits(code.data_qubits, PauliZ)

    def compile_one_round(self, round: [Check], initial_timestep: int):
        for check in round:
            stabilizer = set()
            for operator in check.operators:
                stabilizer.add(operator.pauli.name)

            if stabilizer == {'Z'}:

                self.initialize_qubits(
                    [check.ancilla], initial_timestep)

            elif stabilizer == {'X'}:
                print('todo')
            elif stabilizer == {'X', 'Z'}:
                raise Exception(
                    'Sorry, mixed stabilizers are not supported.')

            for operator in check.operators:
                self.translate_operator(
                    operator, check.ancilla)
            if stabilizer == {'Z'}:
                self.measure_qubits([check.ancilla], PauliZ)

        return(initial_timestep+len(self.gates_at_timesteps))

    def measure_qubits(self, qubits: [Qubit], basis: Pauli):
        for qubit in qubits:
            timestep = self.find_timestep(qubit)
            # self.gates_at_timesteps[timestep]['gates'][qubit] = "RZ"
            if basis == PauliZ:
                self.gates_at_timesteps[timestep]['gates'][qubit] = 'MRZ'
            elif basis == PauliX:
                self.gates_at_timesteps[timestep]['gates'][qubit] = 'MRX'
            elif basis == PauliY:
                self.gates_at_timesteps[timestep]['gates'][qubit] = 'MRY'
            self.gates_at_timesteps[timestep]['initialized_qubits'].remove(
                qubit)

    def initialize_qubits(self, qubits: [Qubit], timestep):
        if timestep not in self.gates_at_timesteps:
            self.gates_at_timesteps[timestep] = copy.deepcopy(empty_timestep)
            self.gates_at_timesteps[timestep]['initialized_qubits'] = copy.copy(
                self.gates_at_timesteps[timestep-1]['initialized_qubits'])

        for qubit in qubits:
            # TODOtimestep = self.find_timestep(qubit)

            if qubit not in self.gates_at_timesteps[timestep]['initialized_qubits']:
                if qubit.initial_state == State(0):
                    self.gates_at_timesteps[timestep]['gates'][qubit] = "RZ"
                self.gates_at_timesteps[timestep]['occupied_qubits'].add(
                    qubit)
                for future_timestep in range(timestep, len(self.gates_at_timesteps)):
                    self.gates_at_timesteps[future_timestep]['initialized_qubits'].add(
                        qubit)

    def translate_operator(self, operator: Operator, ancilla: Qubit):
        if operator.pauli == PauliZ:
            timestep_control = self.find_timestep(ancilla)
            timestep_target = self.find_timestep(operator.qubit)
            timestep = max([timestep_control, timestep_target])
            self.gates_at_timesteps[timestep]['occupied_qubits'].add(
                operator.qubit)
            self.gates_at_timesteps[timestep]['occupied_qubits'].add(
                ancilla)

            self.gates_at_timesteps[timestep]['gates'][operator.qubit,
                                                       ancilla] = "CNOT"

    def find_timestep(self, qubit):
        for timestep in range(len(self.gates_at_timesteps.keys())):
            if qubit not in self.gates_at_timesteps[timestep]['occupied_qubits']:
                return(timestep)
        else:

            self.gates_at_timesteps[timestep+1] = copy.deepcopy(empty_timestep)
            self.gates_at_timesteps[timestep+1]['initialized_qubits'] = copy.copy(
                self.gates_at_timesteps[timestep]['initialized_qubits'])
            return(timestep+1)
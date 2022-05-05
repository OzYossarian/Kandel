from main.compiling.NoiseModel import NoiseModel
from main.QPUs.QPU import QPU
from main.compiling.Circuit import Circuit
from main.codes.Code import Code
from main.building_blocks.PauliLetter import PauliX, PauliZ, PauliY
from main.building_blocks.Qubit import Qubit
from main.building_blocks.Pauli import Pauli
from main.building_blocks.Check import Check
from main.enums import State
import copy

empty_timestep = {'occupied_qubits': set(),
                  'initialized_qubits': set(),
                  'gates': dict(),
                  'noise': dict(),
                  'repeat': False}


class Compiler(object):
    def __init__(self, noise_model: NoiseModel = None):
        if noise_model is None:
            self.noise_model = NoiseModel()
        else:
            self.noise_model = noise_model

        self.gates_at_timesteps = dict()
        self.gates_at_timesteps[0] = copy.deepcopy(empty_timestep)
        self.detector_qubits = set()

    def compile_qpu(self, qpu: QPU, circuit: Circuit, n_timesteps: int = 1):
        pass

    def compile_code(
            self, code: Code, repeat_block=True, final_block=True,
            measure_data_qubits=False):
        self.initialize_qubits(code.data_qubits.values(), 0, 'data')

        initial_timestep = 0
        for ancilla_qubit in code.ancilla_qubits.values():
            if ancilla_qubit.initial_state == State.Zero:
                self.detector_qubits.add(ancilla_qubit)

        if self.noise_model.data_qubit_start_round != 0:
            self.add_noise_start_round_data_qubits(
                code.data_qubits.values(), initial_timestep)

        for round in code.schedule:
            initial_timestep = self.compile_one_round(
                round, initial_timestep)

        if repeat_block:
            start_timestep_repeat_block = initial_timestep
            # need to compile two rounds because of repeat block
            if self.noise_model.data_qubit_start_round != 0:
                self.add_noise_start_round_data_qubits(
                    code.data_qubits.values(), initial_timestep)

            for round in code.schedule:
                initial_timestep = self.compile_one_round(
                    round, initial_timestep)

            for t in range(start_timestep_repeat_block, initial_timestep):
                self.gates_at_timesteps[t]['repeat'] = True

        if final_block:
            if self.noise_model.data_qubit_start_round != 0:
                self.add_noise_start_round_data_qubits(
                    code.data_qubits.values(), initial_timestep)
            for round in code.schedule:
                initial_timestep = self.compile_one_round(
                    round, initial_timestep)

        if measure_data_qubits:
            self.measure_data_qubits(code,
                                     PauliZ,
                                     timestep=initial_timestep-1)
            self.add_logical_observable(code.logical_operator,
                                        PauliZ,
                                        timestep=initial_timestep-1)

        if self.noise_model.idling_noise != 0:
            self.add_idling_noise()

    def add_idling_noise(self):
        for timestep in self.gates_at_timesteps:
            for qubit in self.gates_at_timesteps[timestep]['initialized_qubits']:
                if qubit not in self.gates_at_timesteps[timestep]['occupied_qubits']:
                    if qubit in self.gates_at_timesteps[timestep]['noise']:
                        self.gates_at_timesteps[timestep]['noise'][qubit].append(
                            self.noise_model.idling_noise)
                    else:
                        self.gates_at_timesteps[timestep]['noise'][qubit] = [
                            self.noise_model.idling_noise]

    def add_noise_start_round_data_qubits(self, data_qubits, timestep):
        if timestep not in self.gates_at_timesteps:
            self.gates_at_timesteps[timestep] = copy.deepcopy(empty_timestep)
            self.gates_at_timesteps[timestep]['initialized_qubits'] = copy.copy(
                self.gates_at_timesteps[timestep-1]['initialized_qubits'])
        for qubit in data_qubits:
            self.gates_at_timesteps[timestep]['noise'][qubit] = [
                self.noise_model.data_qubit_start_round]

    def compile_one_round(self, round: [Check], initial_timestep: int):
        for check in round:
            self.initialize_qubits(
                [check.ancilla], initial_timestep +
                check.initialization_timestep)

            for pauli in check.paulis:

                self.translate_pauli(
                    pauli, check.ancilla)

            measurement_timestep = len(check.paulis) + \
                                   initial_timestep + check.initialization_timestep

            self.measure_ancilla_qubit(
                check.ancilla, measurement_timestep)

        return(len(self.gates_at_timesteps))

    def measure_ancilla_qubit(self, qubit: Qubit, timestep):
        timestep = self.find_timestep(qubit, timestep)

        if qubit.initial_state == State.Zero:
            self.gates_at_timesteps[timestep]['gates'][qubit] = 'MRZ'

            if self.noise_model.ancilla_qubit_MZ != 0:
                self.gates_at_timesteps[timestep -
                                        1]['noise'][qubit] = [self.noise_model.ancilla_qubit_MZ]

        elif qubit.initial_state == State.Plus:
            self.gates_at_timesteps[timestep]['gates'][qubit] = "H"
            self.gates_at_timesteps[timestep]['occupied_qubits'].add(
                qubit)
            if timestep+1 not in self.gates_at_timesteps:
                self.gates_at_timesteps[timestep +
                                        1] = copy.deepcopy(empty_timestep)
                self.gates_at_timesteps[timestep+1]['initialized_qubits'] = copy.copy(
                    self.gates_at_timesteps[timestep]['initialized_qubits'])

            if self.noise_model.single_qubit_gate != 0:
                self.gates_at_timesteps[timestep]['noise'][qubit] = [
                    self.noise_model.single_qubit_gate]

            if self.noise_model.ancilla_qubit_MZ != 0:
                if qubit not in self.gates_at_timesteps[timestep]['noise']:
                    self.gates_at_timesteps[timestep]['noise'][qubit] = [
                        self.noise_model.ancilla_qubit_MZ]
                else:
                    self.gates_at_timesteps[timestep]['noise'][qubit].append(
                        self.noise_model.ancilla_qubit_MZ)

            self.gates_at_timesteps[timestep+1]['occupied_qubits'].add(
                qubit)
            self.gates_at_timesteps[timestep+1]['gates'][qubit] = 'MRZ'

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
            data_qubits_measured = tuple()

            for pauli in check.paulis:

                # because there is an overlap
                if pauli.qubit in self.gates_at_timesteps[timestep]['initialized_qubits']:
                    qubits_to_measure += (pauli.qubit, )
                else:
                    data_qubits_measured += (pauli.qubit,)

            qubits = (qubits_to_measure, data_qubits_measured,
                      check.ancilla)

            # add case where data qubits are already measured!
            if basis == PauliZ:
                self.gates_at_timesteps[timestep]['gates'][qubits] = 'MRZ'
            elif basis == PauliX:
                self.gates_at_timesteps[timestep]['gates'][qubits] = 'MRX'
            elif basis == PauliY:
                self.gates_at_timesteps[timestep]['gates'][qubits] = 'MRY'

            for qubit in qubits_to_measure:
                if self.noise_model.data_qubit_MZ != 0:
                    if qubit in self.gates_at_timesteps[timestep-1]['noise']:
                        self.gates_at_timesteps[timestep-1]['noise'][qubit].append(
                            self.noise_model.data_qubit_MZ)
                    else:
                        self.gates_at_timesteps[timestep -
                                                1]['noise'][qubit] = [self.noise_model.data_qubit_MZ]
                self.gates_at_timesteps[timestep]['occupied_qubits'].add(
                    qubit)

                for future_timestep in range(timestep, len(self.gates_at_timesteps)):
                    self.gates_at_timesteps[future_timestep]['initialized_qubits'].remove(
                        qubit)

    def add_logical_observable(self, logical_op: [Pauli], basis: PauliZ, timestep: int):
        qubits = tuple()
        for pauli in logical_op:
            qubits += (pauli.qubit,)
        self.gates_at_timesteps[timestep]['gates'][qubits] = "Observable"

    def initialize_qubits(self, qubits: [Qubit], timestep: int, qubit_type='ancilla'):
        if timestep not in self.gates_at_timesteps:
            for i in range(-(timestep-len(self.gates_at_timesteps)), 2):
                self.gates_at_timesteps[timestep +
                                        i] = copy.deepcopy(empty_timestep)
                self.gates_at_timesteps[timestep+i]['initialized_qubits'] = copy.copy(
                    self.gates_at_timesteps[timestep-1+i]['initialized_qubits'])

        for qubit in qubits:
            if qubit not in self.gates_at_timesteps[timestep]['initialized_qubits']:

                if qubit_type == 'data' and self.noise_model.data_qubit_RZ != 0:
                    self.gates_at_timesteps[timestep]['noise'][qubit] = [
                        self.noise_model.data_qubit_RZ]
                elif qubit_type == 'ancilla' and self.noise_model.ancilla_qubit_RZ != 0:
                    self.gates_at_timesteps[timestep]['noise'][qubit] = [
                        self.noise_model.ancilla_qubit_RZ]

                if qubit.initial_state == State.Zero:

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
                    if self.noise_model.single_qubit_gate != 0:
                        self.gates_at_timesteps[timestep +
                                                1]['noise'][qubit] = [self.noise_model.single_qubit_gate]

                for future_timestep in range(timestep, len(self.gates_at_timesteps)):
                    self.gates_at_timesteps[future_timestep]['initialized_qubits'].add(
                        qubit)

    def translate_pauli(self, pauli: Pauli, ancilla: Qubit):
        timestep_ancilla = self.find_timestep(ancilla)
        timestep_data_qubit = self.find_timestep(pauli.qubit)
        timestep = max([timestep_ancilla, timestep_data_qubit])

        self.gates_at_timesteps[timestep]['occupied_qubits'].add(
            pauli.qubit)
        self.gates_at_timesteps[timestep]['occupied_qubits'].add(
            ancilla)

        if self.noise_model.two_qubit_gate != 0:
            self.gates_at_timesteps[timestep]['noise'][(
                pauli.qubit, ancilla)] = [self.noise_model.two_qubit_gate]

        if pauli.letter == PauliZ:
            self.gates_at_timesteps[timestep]['gates'][pauli.qubit,
                                                       ancilla] = "CNOT"
        if pauli.letter == PauliX:
            # assuming the ancilla qubit is in the |+> state
            self.gates_at_timesteps[timestep]['gates'][ancilla,
                                                       pauli.qubit] = "CNOT"

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

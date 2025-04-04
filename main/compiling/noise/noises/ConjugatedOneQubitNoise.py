from typing import List
from main.building_blocks.Qubit import Qubit
from main.compiling.Instruction import Instruction
from main.compiling.noise.noises.Noise import Noise


class ConjugatedOneQubitNoise(Noise):
    def __init__(self, px: float = 0, py: float = 0, pz: float = 0):
        super().__init__()
        self.px = px
        self.py = py
        self.pz = pz

    @classmethod
    def uniform(cls, p: float):
        q = p / 3
        return cls(q, q, q)

    @property
    def name(self):
        return 'PAULI_CHANNEL_1'

    @property
    def params(self):
        return self.px, self.py, self.pz

    @property
    def params_conjugated(self):
        return self.pz, self.py, self.px
    

    def instruction(self, qubits: List[Qubit]):
        if (qubits[0].coords[0] - qubits[0].coords[1] - 2) % 8 == 0:
            return Instruction(qubits, self.name, self.params_conjugated, is_noise=True)
        else:
            return Instruction(qubits, self.name, self.params, is_noise=True)
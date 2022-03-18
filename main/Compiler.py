from main.QPUs.QPU import QPU
from main.Circuit import Circuit


class Compiler(object):
    def __init__(self, noise_model=None):
        pass

    def compile_schedule(self, qpu: QPU, circuit: Circuit, n_timesteps: int = None):
        print(circuit, 'circuit')

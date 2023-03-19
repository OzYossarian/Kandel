from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.noise.noises.OneBitNoise import OneBitNoise
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise
from main.compiling.noise.noises.TwoQubitNoise import TwoQubitNoise


class SuperconductingInspired(NoiseModel):
    def __init__(
            self, p: float):

        super().__init__(
            gate_idling=OneQubitNoise.uniform(p/10),
            resonator_idling=OneQubitNoise.uniform(2*p),
            two_qubit_gate=TwoQubitNoise.uniform(p),
            one_qubit_gate=OneQubitNoise.uniform(p/10),
            initialisation=OneQubitNoise.uniform(2*p),
            measurement=OneBitNoise.uniform(5*p))
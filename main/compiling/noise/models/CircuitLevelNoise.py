from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.noise.noises.OneBitNoise import OneBitNoise
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise
from main.compiling.noise.noises.TwoQubitNoise import TwoQubitNoise


class CircuitLevelNoise(NoiseModel):
    def __init__(
            self, initialisation: OneQubitNoise | float,
            idling: OneQubitNoise | float,
            one_qubit_gate: OneQubitNoise | float,
            two_qubit_gate: TwoQubitNoise | float,
            measurement: OneBitNoise | float):

        super().__init__(
            initialisation=initialisation,
            idling=idling,
            one_qubit_gate=one_qubit_gate,
            two_qubit_gate=two_qubit_gate,
            measurement=measurement)

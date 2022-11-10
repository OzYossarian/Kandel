from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.noise.noises.OneBitNoise import OneBitNoise
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise


class PhenomenologicalNoise(NoiseModel):
    def __init__(
            self, data_qubit: OneQubitNoise | float | None,
            measurement: OneBitNoise | float | None):

        super().__init__(
            data_qubit_start_round=data_qubit,
            measurement=measurement)
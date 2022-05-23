from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.noise.noises.MeasurementNoise import MeasurementNoise
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise


class PhenomenologicalNoise(NoiseModel):
    def __init__(
            self, data_qubit: OneQubitNoise | float,
            measurement: MeasurementNoise | float):

        super().__init__(
            data_qubit_start_round=data_qubit,
            measurement=measurement)
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise


class CodeCapacityNoise(NoiseModel):
    def __init__(self, px, py, pz: float):
        super().__init__(data_qubit_start_round=OneQubitNoise(px=px, py=py, pz=pz))

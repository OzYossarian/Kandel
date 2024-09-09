from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.noise.noises.ConjugatedOneQubitNoise import ConjugatedOneQubitNoise

class DomainWallCodeCapacityNoise(NoiseModel):
    def __init__(self, px, py, pz: float):
        super().__init__(data_qubit_start_round=ConjugatedOneQubitNoise(px=px, py=py, pz=pz))
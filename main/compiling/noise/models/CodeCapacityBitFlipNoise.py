from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise


class CodeCapacityBitFlipNoise(NoiseModel):
    """Noise channel that applies Pauli X to data qubits.

    Args:
        NoiseModel: OneQubitNoise or float that acts on data qubits at the start of each round.
    """
    def __init__(self, bit_flip_probability: float):
        bit_flip_noise = OneQubitNoise(px=bit_flip_probability)
        super().__init__(data_qubit_start_round=bit_flip_noise)


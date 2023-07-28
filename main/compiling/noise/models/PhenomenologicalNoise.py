from typing import Union
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.noise.noises.OneBitNoise import OneBitNoise
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise


class PhenomenologicalNoise(NoiseModel):
    """Noise channel where noise can be added to measurements and data qubits.

    Args:
        data_qubit: OneQubitNoise or float that acts on data qubits at the start of each round.
        measurement: OneBitNoise or float that flips measurement results.
    """
    def __init__(
            self, data_qubit: Union[OneQubitNoise, float, None] = None,
            measurement: Union[OneBitNoise, float, None] = None):
        super().__init__(
            data_qubit_start_round=data_qubit,
            measurement=measurement)

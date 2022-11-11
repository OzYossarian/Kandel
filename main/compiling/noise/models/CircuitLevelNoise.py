from typing import Union
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.noise.noises.OneBitNoise import OneBitNoise
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise
from main.compiling.noise.noises.TwoQubitNoise import TwoQubitNoise


class CircuitLevelNoise(NoiseModel):
    def __init__(
            self, initialisation: Union[OneQubitNoise,float,None],
            idling: Union[OneQubitNoise,float ,None],
            one_qubit_gate: Union[OneQubitNoise, float , None],
            two_qubit_gate: Union[TwoQubitNoise , float , None],
            measurement: Union[OneBitNoise , float , None]):

        super().__init__(
            initialisation=initialisation,
            idling=idling,
            one_qubit_gate=one_qubit_gate,
            two_qubit_gate=two_qubit_gate,
            measurement=measurement)

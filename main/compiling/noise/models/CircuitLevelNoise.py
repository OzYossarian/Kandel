from typing import Union
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.noise.noises.OneBitNoise import OneBitNoise
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise
from main.compiling.noise.noises.TwoQubitNoise import TwoQubitNoise


class CircuitLevelNoise(NoiseModel):
    """Noise channel where noise can be added to any location.

    Args:
        initialisation: OneQubitNoise or float that acts after initialization.
        idling: OneQubitNoise or float that acts after initialization.
        one_qubit_gate: OneQubitNoise or float that acts after a gate on one qubit
        two_qubit_gate: TwoQubitNoise or float that acts after two qubit gates.
        measurement: OneBitNoise or float that flips measurement resutls.
    """
    def __init__(
            self, initialisation: Union[OneQubitNoise, float, None] = None,
            idling: Union[OneQubitNoise, float, None] = None,
            one_qubit_gate: Union[OneQubitNoise, float, None] = None,
            two_qubit_gate: Union[TwoQubitNoise, float, None] = None,
            measurement: Union[OneBitNoise, float, None] = None):
        super().__init__(
            initialisation=initialisation,
            idling=idling,
            one_qubit_gate=one_qubit_gate,
            two_qubit_gate=two_qubit_gate,
            measurement=measurement)

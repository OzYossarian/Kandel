from typing import Union
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.noise.noises.OneBitNoise import OneBitNoise
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise
from main.compiling.noise.noises.TwoQubitNoise import TwoQubitNoise


class SI1000(NoiseModel):
    """Noise model from https://quantum-journal.org/papers/q-2021-12-20-605/

    Args:
        initialisation: OneQubitNoise or float that acts after initialization.
        idling: OneQubitNoise or float that acts after initialization.
        one_qubit_gate: OneQubitNoise or float that acts after a gate on one qubit
        two_qubit_gate: TwoQubitNoise or float that acts after two qubit gates.
        measurement: OneBitNoise or float that flips measurement resutls.
    """

    def __init__(
            self,
            p: float):
        super().__init__(
            # 3 such that the sum of the two errors that act non trivially is 1.
            initialisation=3*p,
            idling=2*p,
            one_qubit_gate=p/10,
            two_qubit_gate=p,
            measurement=5*p,
            resonator_idle=2*p,
        )

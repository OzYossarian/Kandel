from typing import Type

from main.compiling.noise.noises.OneBitNoise import OneBitNoise
from main.compiling.noise.noises.Noise import Noise
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise
from main.compiling.noise.noises.TwoQubitNoise import TwoQubitNoise


class NoiseModel:
    def __init__(
            self, initialisation: OneQubitNoise | float | int = None,
            idling: OneQubitNoise | float | int = None,
            data_qubit_start_round: OneQubitNoise | float | int = None,
            one_qubit_gate: OneQubitNoise | float | int = None,
            two_qubit_gate: TwoQubitNoise | float | int = None,
            measurement: OneBitNoise | float | int = None):

        self.initialisation: OneQubitNoise | None = \
            self.default_to_uniform_noise(initialisation, OneQubitNoise)
        self.idling: OneQubitNoise | None = \
            self.default_to_uniform_noise(idling, OneQubitNoise)
        self.data_qubit_start_round: OneQubitNoise | None = \
            self.default_to_uniform_noise(data_qubit_start_round, OneQubitNoise)
        self.one_qubit_gate: OneQubitNoise | None = \
            self.default_to_uniform_noise(one_qubit_gate, OneQubitNoise)
        self.two_qubit_gate: TwoQubitNoise | None = \
            self.default_to_uniform_noise(two_qubit_gate, TwoQubitNoise)
        self.measurement: OneBitNoise | None = \
            self.default_to_uniform_noise(measurement, OneBitNoise)

    @staticmethod
    def default_to_uniform_noise(arg, noise: Type[Noise]):
        # If user has given a float or int, we should default to a uniform
        # noise of the required type with the given float/int as argument.
        # If not, user must have given either a Noise object or None; in
        # both cases, just return this.
        return arg if not isinstance(arg, float | int) else noise.uniform(arg)

from typing import Type, Union

from main.compiling.noise.noises.OneBitNoise import OneBitNoise
from main.compiling.noise.noises.Noise import Noise
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise
from main.compiling.noise.noises.TwoQubitNoise import TwoQubitNoise


class NoiseModel:
    def __init__(
            self, initialisation: Union[OneQubitNoise, float, int] = None,
            idling: Union[OneQubitNoise, float, int] = None,
            data_qubit_start_round: Union[OneQubitNoise, float, int] = None,
            one_qubit_gate: Union[OneQubitNoise, float, int] = None,
            two_qubit_gate: Union[TwoQubitNoise, float, int] = None,
            measurement: Union[OneBitNoise, float, int] = None,
            resonator_idle: Union[OneQubitNoise, float, int] = None,):

        self.initialisation: Union[OneQubitNoise, None] = \
            self.default_to_uniform_noise(initialisation, OneQubitNoise)
        
        self.idling: Union[OneQubitNoise, None] = \
            self.default_to_uniform_noise(idling, OneQubitNoise)
        self.data_qubit_start_round: Union[OneQubitNoise, None] = \
            self.default_to_uniform_noise(data_qubit_start_round, OneQubitNoise)
        self.one_qubit_gate: Union[OneQubitNoise, None] = \
            self.default_to_uniform_noise(one_qubit_gate, OneQubitNoise)
        self.two_qubit_gate: Union[TwoQubitNoise, None] = \
            self.default_to_uniform_noise(two_qubit_gate, TwoQubitNoise)
        self.measurement: Union[OneBitNoise, None] = \
            self.default_to_uniform_noise(measurement, OneBitNoise)
        self.resonator_idle: Union[OneQubitNoise, None] = \
            self.default_to_uniform_noise(resonator_idle, OneQubitNoise)
        
    @staticmethod
    def default_to_uniform_noise(arg, noise: Type[Noise]):
        # If user has given a float or int, we should default to a uniform
        # noise of the required type with the given float/int as argument.
        # If not, user must have given either a Noise object or None; in
        # both cases, just return this.
        if not isinstance(arg, float) and not isinstance(arg, int):
            return arg
        else:
            return noise.uniform(arg)

    def __eq__(self, other):
        return \
            type(self) == type(other) and \
            self.initialisation == other.initialisation and \
            self.idling == other.idling and \
            self.data_qubit_start_round == other.data_qubit_start_round and \
            self.one_qubit_gate == other.one_qubit_gate and \
            self.two_qubit_gate == other.two_qubit_gate and \
            self.measurement == other.measurement

    def __hash__(self):
        return hash((
            self.initialisation,
            self.idling,
            self.data_qubit_start_round,
            self.one_qubit_gate,
            self.two_qubit_gate,
            self.measurement))

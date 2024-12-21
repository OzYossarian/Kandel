from typing import List, Tuple, Type, Union

from main.compiling.noise.noises.OneBitNoise import OneBitNoise
from main.compiling.noise.noises.Noise import Noise
from main.compiling.noise.noises.OneQubitNoise import OneQubitNoise
from main.compiling.noise.noises.TwoQubitNoise import TwoQubitNoise


class NoiseModel:
    def __init__(self, **kwargs):
        noise_types = {
            'initialisation': OneQubitNoise,
            'idling': OneQubitNoise,
            'data_qubit_start_round': OneQubitNoise,
            'one_qubit_gate': OneQubitNoise,
            'two_qubit_gate': TwoQubitNoise,
            'measurement': OneBitNoise,
            'resonator_idle': OneQubitNoise,
            'before_mpp_noise': TwoQubitNoise,
        }

        for key, noise_type in noise_types.items():
            setattr(self, key, self.default_to_uniform_noise(
                kwargs.get(key), noise_type))

    @staticmethod
    def default_to_uniform_noise(arg, noise: Union[Type[Noise], List[Type[Noise]]]):
        if not isinstance(arg, (float, int)):
            return arg
        if isinstance(noise, list):
            return [n.uniform(arg) for n in noise]
        return noise.uniform(arg)

    def __eq__(self, other):
        return all(
            getattr(self, attr) == getattr(other, attr)
            for attr in self.__dict__
        )

    def __hash__(self):
        return hash(tuple(getattr(self, attr) for attr in self.__dict__))

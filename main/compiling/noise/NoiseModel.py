from typing import Dict, Type

from main.compiling.noise.MeasurementNoise import MeasurementNoise
from main.compiling.noise.Noise import Noise
from main.compiling.noise.OneQubitNoise import OneQubitNoise
from main.compiling.noise.TwoQubitNoise import TwoQubitNoise


class NoiseModel:
    def __init__(
            self, initialisation: OneQubitNoise | float = None,
            idling: OneQubitNoise | float = None,
            data_qubit_start_round: OneQubitNoise | float = None,
            one_qubit_gate: OneQubitNoise | float = None,
            two_qubit_gate: TwoQubitNoise | float = None,
            measurement: OneQubitNoise | float = None):

        def default_to_uniform_noise(arg, noise: Type[Noise]):
            return arg if not isinstance(arg, float) else noise.uniform(arg)

        self.initialisation: Noise = \
            default_to_uniform_noise(initialisation, OneQubitNoise)
        self.idling: Noise = \
            default_to_uniform_noise(idling, OneQubitNoise)
        self.data_qubit_start_round: Noise = \
            default_to_uniform_noise(data_qubit_start_round, OneQubitNoise)
        self.one_qubit_gate: Noise = \
            default_to_uniform_noise(one_qubit_gate, OneQubitNoise)
        self.two_qubit_gate: Noise = \
            default_to_uniform_noise(two_qubit_gate, TwoQubitNoise)
        self.measurement: Noise = \
            default_to_uniform_noise(measurement, MeasurementNoise)


class CodeCapacityBitFlipNoise(NoiseModel):
    def __init__(self, bit_flip_probability: float):
        bit_flip_noise = OneQubitNoise(px=bit_flip_probability)
        super().__init__(data_qubit_start_round=bit_flip_noise)


class PhenomenologicalNoise(NoiseModel):
    def __init__(
            self, data_qubit: OneQubitNoise | float,
            measurement: MeasurementNoise | float):

        super().__init__(
            data_qubit_start_round=data_qubit,
            measurement=measurement)


class CircuitLevelNoise(NoiseModel):
    def __init__(
            self, initialisation: OneQubitNoise | float,
            idling: OneQubitNoise | float,
            one_qubit_gate: OneQubitNoise | float,
            two_qubit_gate: TwoQubitNoise | float,
            measurement: MeasurementNoise | float):

        super().__init__(
            initialisation=initialisation,
            idling=idling,
            one_qubit_gate=one_qubit_gate,
            two_qubit_gate=two_qubit_gate,
            measurement=measurement)

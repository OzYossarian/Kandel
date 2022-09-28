from typing import Tuple

from main.compiling.noise.noises.Noise import Noise


class MockNoise(Noise):
    def __init__(self, name: str, params: Tuple[float, ...] | float):
        self._name = name
        self._params = params
        super().__init__()

    @classmethod
    def uniform(cls, p: float):
        return cls('MOCK_NOISE', p)

    @property
    def name(self) -> str:
        return self._name

    @property
    def params(self) -> Tuple[float, ...]:
        return self._params

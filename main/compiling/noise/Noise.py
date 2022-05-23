from abc import abstractmethod, ABC
from typing import Tuple, List

from main.building_blocks.Qubit import Qubit
from main.compiling.Gate import Gate


class Noise(ABC):
    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def uniform(cls, p: float):
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def params(self) -> Tuple[float, ...]:
        pass

    @property
    def instruction(self) -> Tuple[str, Tuple[float, ...]]:
        return self.name, self.params

    def gate(self, qubits: List[Qubit]):
        return Gate(qubits, self.name, self.params, is_noise=True)

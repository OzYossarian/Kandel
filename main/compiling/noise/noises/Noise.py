from abc import abstractmethod, ABC
from typing import Tuple, List

from main.building_blocks.Qubit import Qubit
from main.compiling.Instruction import Instruction


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

    def instruction(self, qubits: List[Qubit]):
        return Instruction(qubits, self.name, self.params, is_noise=True)

from abc import abstractmethod, ABC
from typing import Tuple, List, Any, Union

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
    def params(self) -> Union[Tuple[float, ...], float]:
        pass

    def instruction(self, qubits: List[Qubit]):
        return Instruction(qubits, self.name, self.params, is_noise=True)

    def __eq__(self, other: Any):
        return \
            type(self) == type(other) and \
            self.name == other.name and \
            self.params == other.params

    def __hash__(self):
        return hash((self.name, self.params))


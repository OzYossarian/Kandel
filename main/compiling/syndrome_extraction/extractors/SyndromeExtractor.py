from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, TYPE_CHECKING

from main.building_blocks.Check import Check
from main.compiling.Circuit import Circuit
if TYPE_CHECKING:
    from main.compiling.compilers.Compiler import Compiler
from main.utils.types import Tick


class SyndromeExtractor(ABC):
    def __init__(self, parallelize: bool = True):
        """
        Base class for all syndrome extractors.

        Args:
            parallelize:
                Whether to extract all checks' syndromes for a given round in
                parallel.
        """
        self.parallelize = parallelize

    @abstractmethod
    def extract_checks(
            self,
            checks: Iterable[Check],
            round: int,
            tick: int,
            circuit: Circuit,
            compiler: Compiler) -> Tick:
        pass

from __future__ import annotations

from typing import Iterable, TYPE_CHECKING

from main.building_blocks.Check import Check
from main.compiling.Circuit import Circuit
if TYPE_CHECKING:
    from main.compiling.compilers.Compiler import Compiler
from main.compiling.syndrome_extraction.extractors import SyndromeExtractor
from main.utils.types import Tick


class NativePauliProductMeasurementsExtractor(SyndromeExtractor):
    def __init__(self, parallelize: bool = True):
        """
        A syndrome extractor that can use native Pauli product measurements.

        Args:
            parallelize:
                Whether to extract all checks' syndromes for a given round in
                parallel.
        """
        super().__init__(parallelize)

    def extract_checks(
            self,
            checks: Iterable[Check],
            round: int,
            tick: int,
            circuit: Circuit,
            compiler: Compiler) -> Tick:
        raise NotImplementedError()

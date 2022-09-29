from typing import Iterable

from main.building_blocks.Check import Check
from main.compiling.Circuit import Circuit
from main.compiling.compilers.Compiler import Compiler
from main.compiling.syndrome_extraction.extractors import SyndromeExtractor
from main.utils.types import Tick


class MockSyndromeExtractor(SyndromeExtractor):
    def __init__(self, parallelize: bool):
        super().__init__(parallelize)

    def extract_checks(
            self,
            checks: Iterable[Check],
            round: int,
            tick: int,
            circuit: Circuit,
            compiler: Compiler) -> Tick:
        raise NotImplementedError()


def test_syndrome_extractor_init():
    # Right now there's only one property to save
    parallelize = True
    extractor = MockSyndromeExtractor(parallelize)
    assert extractor.parallelize == parallelize

    parallelize = False
    extractor = MockSyndromeExtractor(parallelize)
    assert extractor.parallelize == parallelize




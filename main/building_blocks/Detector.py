from typing import List, Tuple

from main.building_blocks.Check import Check


class Detector:
    def __init__(
            self, floor: List[Tuple[int, Check]],
            lid: List[Tuple[int, Check]]):
        """If we learn the value of the same stabilizer at two different
        timesteps, and the stabilizer remained stabilized in this interval,
        then we can multiply together the two values to detect whether an
        error occurred in this interval. This is what a Detector represents:
        its floor is the set of checks multiplied together to tell us the
        value of the stabilizer the first time around, then the lid is the
        set of checks multiplied together to tell us the value of the
        stabilizer the second time around.
        """
        self.floor = floor
        self.lid = lid






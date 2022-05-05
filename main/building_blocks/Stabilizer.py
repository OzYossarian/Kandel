from typing import List

from main.building_blocks.Check import Check


class Stabilizer:
    def __init__(self, checks: List[Check]):
        self.checks = checks

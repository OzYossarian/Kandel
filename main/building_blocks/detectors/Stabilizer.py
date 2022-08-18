from typing import List

from main.building_blocks.Qubit import Coordinates
from main.building_blocks.detectors.Detector import Detector, TimedCheck


class Stabilizer(Detector):
    def __init__(
            self, timed_checks: List[TimedCheck], end: int,
            anchor: Coordinates = None):
        """
        Specific type of detector, used when we want to measure something
        that we know is at that point in the code's stabilizer group.
            Currently this actually has no more functionality than the
        Detector base class, so is really just a more suggestive name.
        Args:
            timed_checks:
                the timed checks that together make up the stabilizer
            end:
                the first round (modulo schedule length) by which ALL of the
                checks in the stabilizer will have been measured.
            anchor:
                coordinates at which to 'anchor' this stabilizer. If None,
                defaults to the midpoint of the anchors of all checks
                involved.
        """
        super().__init__(timed_checks, end, anchor)

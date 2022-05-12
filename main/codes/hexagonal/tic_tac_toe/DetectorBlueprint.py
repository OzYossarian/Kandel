from collections import Counter
from typing import List, Tuple

from main.Colour import Colour
from main.building_blocks.PauliLetter import PauliLetter
from main.utils.DebugFriendly import DebugFriendly
from main.utils.utils import modulo_duplicates


class DetectorBlueprint(DebugFriendly):
    def __init__(
            self, schedule_length: int, learned: int,
            floor: List[Tuple[int, Colour, PauliLetter]],
            lid: List[Tuple[int, Colour, PauliLetter]]):
        """An actual Detector object essentially consists of a set of Check
        objects. This class instead specifies how to build a particular
        family of Detector objects.

        Args:
            schedule_length:
                length of tic-tac-toe route and thus size of the repeating
                portion of the code.
            learned:
                time at which this detector can be fully known, i.e. time
                at which final checks are measured.
            floor:
                a list of tuples (t, colour, letter) which specifies which
                check types (colour, letter) consititute the floor of the
                detector, and when they are measured (t).
            lid:
                as above, but replace the word floor with lid.
        """

        # Multiplying together the outcomes of same two checks always gives 1,
        # so we are only interested in these checks modulo 2.
        checks = modulo_duplicates(floor + lid, 2)

        # At the moment the t in each (t, colour, letter) denotes when this
        # check type is first measured. It is instead more helpful for it to
        # denote how many timesteps ago the checks were measured, relative to
        # when the final set of checks in this detector were measured.
        def relative_to_when_detector_is_learned(face):
            return [
                (t - learned, colour, letter)
                for (t, colour, letter) in face
                if (t, colour, letter) in checks]

        self.floor = relative_to_when_detector_is_learned(floor)
        self.lid = relative_to_when_detector_is_learned(lid)
        self.checks = self.floor + self.lid
        self.learned = learned % schedule_length
        self.repr_keys = ['learned', 'floor', 'lid']

    def equivalent_to(self, other):
        """ If another detector contains the same checks as this one, measured
        at the same times (regardless of whether they're in the floor or lid)
        then these detectors both tell us exactly the same information.
        """
        return \
            isinstance(other, DetectorBlueprint) and \
            self.learned == other.learned and \
            Counter(self.checks) == Counter(other.checks)

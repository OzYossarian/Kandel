from typing import List, Tuple

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Coordinates
from main.building_blocks.detectors.Detector import Detector


class Stabilizer(Detector):
    def __init__(
            self, lid: List[Tuple[int, Check]], end: int,
            anchor: Coordinates = None):
        """ Usually a detector measures the same Pauli product at two
        different times (floor and lid) and then compares the two.
        Occasionally a detector need not have a floor - i.e. if we've just
        initialised some qubits, there are Pauli products we know should give
        deterministic results, if we were to measure them. An example - if we
        initialise two qubits in the zero state, then measuring ZZ should give
        us 1 deterministically. In other words, we know ZZ is just a
        stabilizer at this point.
          This class represents this sort of detector - ones that are in fact
        just measuring an existing known stabilizer."""
        super().__init__([], lid, end, anchor)
        # TODO - remove!
        self.negate = False

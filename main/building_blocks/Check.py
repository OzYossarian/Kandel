from typing import List

from main.Colour import Colour
from main.building_blocks.Pauli import Pauli
from main.building_blocks.Qubit import Qubit, Coordinates
from main.utils.DebugFriendly import DebugFriendly


class Check(DebugFriendly):
    def __init__(
            self, paulis: List[Pauli], anchor: Coordinates = None,
             colour: Colour = None, ancilla: Qubit = None):
        """A check is a Pauli operator that is actually measured as part of
        the code. In some codes the checks are just the stabilizers (e.g.
        surface code, colour code), but this need not be the case (e.g.
        Floquet codes).

        Args:
            paulis:
                The Paulis (data qubit + Pauli letter) that make up this check
            anchor:
                In some sense its center, but need not actually be the
                midpoint of all the data qubits involved. Used for
                distinguishing otherwise identical checks - e.g. on a rotated
                surface code, the weight-2 checks along the top and bottom
            ancilla:
                The ancilla qubit used for syndrome extraction, if it exists.
            colour:
                If it exists, the colour assigned to this check - e.g. in the
                colour code, each edge and each hexagon gets a colour.
        """
        self.paulis = paulis
        self.anchor = anchor
        self.colour = colour
        # Which detectors (if any) this check triggers - i.e. is this check
        # part of a final set of checks that need to be measured before a
        # detector can be learned.
        self.detectors_triggered = []

        # The following properties are set by a compiler. The 'measurements'
        # attribute notes down, for any given round number, where the
        # measurement of this check came in the ordering of all measurements
        # performed on the code, according to Stim.
        self.ancilla = ancilla
        self.measurements = {}

        super().__init__(['paulis', 'colour'])

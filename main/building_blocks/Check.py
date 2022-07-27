from typing import List, Dict

from main.Colour import Colour
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.Qubit import Coordinates
from main.utils.NiceRepr import NiceRepr


class Check(NiceRepr):
    def __init__(
            self, paulis: Dict[Coordinates, Pauli],
            anchor: Coordinates = None, colour: Colour = None):
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
            colour:
                If it exists, the colour assigned to this check - e.g. in the
                colour code, each edge and each hexagon gets a colour.
        """
        self.paulis = paulis
        self.anchor = anchor
        self.colour = colour
        self.weight = len(paulis)

        # The following properties are set by a compiler.
        self.ancilla = None

        super().__init__(['paulis', 'colour'])

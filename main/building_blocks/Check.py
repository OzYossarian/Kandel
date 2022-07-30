from typing import List, Dict

from main.Colour import Colour
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.Qubit import Coordinates
from main.utils.NiceRepr import NiceRepr
from main.utils.utils import coords_mid, coords_length, coords_minus


class Check(NiceRepr):
    def __init__(
            self, paulis: List[Pauli] | Dict[Coordinates, Pauli],
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
        if isinstance(paulis, dict):
            # Anchor shouldn't be None in this case, because the keys of
            # `paulis` are the offsets of the paulis from the anchor.
            assert anchor is not None
            # Check all offsets have the same dimensions
            coords_lengths = {coords_length(coords) for coords in paulis}
            assert len(coords_lengths) == 1
        else:
            # Auto-create dictionary for paulis
            if anchor is None:
                anchor = coords_mid([pauli.qubit.coords for pauli in paulis])
            paulis = {
                coords_minus(pauli.qubit.coords, anchor): pauli
                for pauli in paulis}

        self.paulis = paulis
        self.anchor = anchor
        self.colour = colour
        self.weight = len(paulis)
        self.dimension = coords_length(self.anchor)

        # The following properties are set by a compiler.
        self.ancilla = None

        super().__init__(['paulis', 'colour'])

from typing import List

from main.Colour import Colour
from main.building_blocks.Pauli import Pauli
from main.building_blocks.Qubit import Qubit, Coordinates
from main.utils.DebugFriendly import DebugFriendly


class Check(DebugFriendly):
    def __init__(
            self, paulis: List[Pauli], anchor: Coordinates = None,
            ancilla: Qubit = None, colour: Colour = None,
            initialization_timestep: int = 0):
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
            initialization_timestep:
                TODO - remove this, and have a separate class that does
                 syndrome extraction.
                Relative timestep at which this check starts its syndrome
                extraction circuit. e.g. in the rotated surface code, each
                check requires up to 4 CNOTs to extract a syndrome, placed
                at timesteps 0, 1, 2 and 3. Some weight-2 checks have these
                CNOTs at timesteps 0 and 1, while some have them at timesteps
                2 and 3, etc.
        """
        self.paulis = paulis
        self.anchor = anchor
        self.colour = colour
        self.ancilla = ancilla
        self.initialization_timestep = initialization_timestep
        super().__init__(['paulis', 'colour'])

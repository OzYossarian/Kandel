from abc import ABC, abstractmethod
from typing import List

from main.building_blocks.Check import Check
from main.building_blocks.pauli.Pauli import Pauli


class ControlledGateOrderer(ABC):
    """
    When extracting a syndrome using an ancilla qubit, controlled gates
    are placed between the ancilla qubit and the data qubits. The order
    in which these gates are placed matters. This base class provides a
    way to define the order in which these gates should occur.
    """
    def __init__(self):
        pass

    @abstractmethod
    def order(self, check: Check) -> List[Pauli | None]:
        """
        Given a check, this returns the check's Paulis in the order in which
        controlled gates should be placed between them and the ancilla. The
        value None is used to keep things in sync - if None is found, the
        compiler should wait for the same number of ticks as it would have
        taken to place a controlled gate (and any pre-/post-rotations
        before/after the controlled gate). This is vital for codes
        with checks of different weights - e.g. in the rotated surface
        code, bulk checks are weight 4, but boundary checks are weight 2
        An example ordering for a weight 2 check might thus be:
          [pauli_1, pauli_2, None, None]
        This would mean controlled gates are placed at timesteps 0 and 1
        of the syndrome extraction round, with nothing placed at timesteps
        2 and 3.

        Args:
            check: the Check whose paulis should be ordered

        Returns:
            A list whose length is equal to the number of timesteps in a
            syndrome extraction round, containing the Check's paulis,
            ordered as described.

        """
        pass

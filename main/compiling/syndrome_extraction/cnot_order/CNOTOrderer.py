from abc import ABC, abstractmethod
from typing import List

from main.building_blocks.Check import Check
from main.building_blocks.Pauli import Pauli


class CNOTOrderer(ABC):
    def __init__(self):
        # When extracting a syndrome, CNOTs between data qubits and ancilla
        # qubit(s) are used. The order of these CNOTs matters - firstly to
        # ensure qubits aren't involved in multiple CNOTs at once, and
        # secondly to ensure errors are detected correctly.
        pass

    @abstractmethod
    def order(self, check: Check) -> List[Pauli | None]:
        # Given a check, this returns the checks Paulis in the order they
        # should have CNOTs to/from ancillas. The value None is used to keep
        # things in sync - if None is found, the compiler should wait for
        # the same number of ticks as it would have taken to place a CNOT
        # (and any gates before/after the CNOT). This is vital for codes
        # with checks of different weights - e.g. in the rotated surface
        # code, bulk checks are weight 4, but boundary checks are weight 2
        # An example ordering for a weight 2 check might thus be:
        #   [None, None, pauli_1, pauli_2]
        pass

from __future__ import annotations

import operator
from collections import defaultdict
from functools import reduce
from typing import Iterable, List

from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ, PauliLetter, PauliX, PauliY
from main.utils.enums import State


def compose(paulis: Iterable[Pauli], identities_removed: bool = False):
    # Order matters because Pauli multiplication is not commutative.
    # We assume 'paulis' is ordered such that the rightmost element is the
    # first to be applied, and the leftmost element is the last to be applied
    # (i.e. the order in which we ordinarily write Paulis algebraically).
    # If two Paulis act on different qubits, it doesn't matter which comes
    # first in the ordering.

    # Group by the qubit that the Paulis are applied to
    grouped_paulis = defaultdict(list)
    for pauli in paulis:
        grouped_paulis[pauli.qubit].append(pauli.letter)
    # Compose together the Paulis on each qubit.
    composed = [
        Pauli(qubit, reduce(lambda x, y: x.compose(y), letters))
        for qubit, letters in grouped_paulis.items()]
    # Omit the identity Paulis, if desired.
    return composed if not identities_removed else remove_identities(composed)


def remove_identities(paulis: List[Pauli]) -> List[Pauli]:
    identities = [
        pauli for pauli in paulis if pauli.letter.letter == 'I']
    non_identities = [
        pauli for pauli in paulis if pauli.letter.letter != 'I']
    identity_sign = reduce(
        operator.mul, [identity.letter.sign for identity in identities], 1)
    if identity_sign == 1:
        # If the identities contribute no sign altogether, remove them.
        return non_identities
    else:
        if len(non_identities) > 0:
            # Transfer the sign of the identities onto a non-identity Pauli
            # and then remove the identities.
            non_identities[0].letter.sign *= identity_sign
            return non_identities
        else:
            raise ValueError(
                "Can't remove identities - they have a non-trivial sign and "
                "there's no non-identity Paulis to transfer this sign onto!"
                f"Given list of Paulis is: {paulis}")


stabilizers = {
    State.Zero: PauliZ,
    State.One: PauliLetter('Z', -1),
    State.Plus: PauliX,
    State.Minus: PauliLetter('X', -1),
    State.I: PauliY,
    State.MinusI: PauliLetter('Y', -1)}

plus_one_eigenstates = {
    PauliZ: State.Zero, 
    PauliLetter('Z', -1): State.One,
    PauliX: State.Plus,
    PauliLetter('X', -1): State.Minus,
    PauliY: State.I,
    PauliLetter('Y', -1): State.MinusI}

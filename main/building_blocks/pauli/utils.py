from __future__ import annotations

import operator
from collections import defaultdict
from functools import reduce
from typing import Iterable, List

from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ, PauliLetter, PauliX, PauliY
from main.enums import State


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
    identity_sign = reduce(
        operator.mul, [identity.letter.sign for identity in identities], 1)
    if identity_sign == 1:
        # If the identities contribute no sign altogether, remove them.
        non_identities = [
            pauli for pauli in paulis if pauli.letter.letter != 'I']
        return non_identities
    else:
        # Otherwise, keep them. There are other things we might consider
        # doing here - e.g. if there's some non-identity Paulis, remove all
        # the identities and transfer their collective sign onto a
        # non-identity Pauli. Or remove all the individual identities whose
        # sign is 1 but keep the rest (those with sign j, -1 or -j). But
        # there's no canonical choice, so to speak, so let's just do nothing.
        return paulis


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

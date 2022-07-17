from __future__ import annotations

import operator
from collections import defaultdict
from functools import reduce
from typing import Iterable

from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ, PauliLetter, PauliX, PauliY, PauliI
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.enums import State


def compose(paulis: Iterable[Pauli]):
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
    # Omit the identity Paulis, if possible.
    identities = [
        pauli for pauli in composed if pauli.letter.letter == 'I']
    identity_sign = reduce(
        operator.mul, [identity.letter.sign for identity in identities], 1)
    if identity_sign == 1:
        non_identities = [
            pauli for pauli in composed if pauli.letter.letter != 'I']
        return non_identities
    else:
        return composed


def get_commutator(a: PauliProduct, b: PauliProduct):
    # Given pauli products a and b, the commutator is aba^(-1)b^(-1). But
    # since all Paulis are self-inverse, this simplifies to abab.
    commutator_paulis = a.paulis + b.paulis + a.paulis + b.paulis
    commutator = PauliProduct(commutator_paulis)
    assert all(letter == 'I' for letter in commutator.word.word)
    assert commutator.word.sign in [1, -1]
    return commutator


def commutes(a: PauliProduct, b: PauliProduct):
    commutator = get_commutator(a, b)
    return commutator.word.sign == 1


stabilizers = {
    State.Zero: PauliZ,
    State.One: PauliLetter('Z', -1),
    State.Plus: PauliX,
    State.Minus: PauliLetter('X', -1),
    State.I: PauliY,
    State.MinusI: PauliLetter('Y', -1)}

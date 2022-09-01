import random

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import TrivialOrderer
from tests.utils.checks import random_check
from tests.utils.numbers import default_test_repeats_medium, default_max_unique_sample_size


def test_trivial_orderer_order():
    # Should just give back whatever we give it.
    orderer = TrivialOrderer()

    # Explicit test:
    paulis = [
        Pauli(Qubit(0), PauliLetter('X')),
        Pauli(Qubit(1), PauliLetter('X')),
        Pauli(Qubit(2), PauliLetter('X'))]
    check = Check(paulis)
    assert orderer.order(check) == paulis

    # Random tests:
    for _ in range(default_test_repeats_medium):
        dimension = random.randint(1, 10)
        max_weight = random.randint(1, 20)
        weight = min(max_weight, default_max_unique_sample_size(dimension))
        check = random_check(
            int_coords=True,
            weight=weight,
            dimension=dimension)
        assert orderer.order(check) == list(check.paulis.values())


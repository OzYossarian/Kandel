import random

import pytest

from main.building_blocks.Qubit import Qubit
from main.compiling.Instruction import Instruction
from tests.utils.utils_numbers import default_test_repeats_small
from tests.building_blocks.utils_qubits import random_qubits


def test_instruction_fails_if_no_qubits_given():
    expected_error = "An instruction must apply to at least one qubit"
    with pytest.raises(ValueError, match=expected_error):
        Instruction([], 'SOME_INSTRUCTION')


def test_instruction_fails_if_qubits_not_unique():
    expected_error = \
        "Can't include the same qubit more than once in an instruction"
    # Explicit test:
    qubit = Qubit(0)
    with pytest.raises(ValueError, match=expected_error):
        Instruction([qubit, qubit], 'SOME_INSTRUCTION')

    # Random tests:
    for _ in range(default_test_repeats_small):
        dimension = random.randint(1, 10)
        num_qubits = random.randint(1, 20)
        qubits = random_qubits(
            num_qubits, int_coords=True, dimension=dimension)
        # Now take a big enough sample from this set of qubits such that
        # we're guaranteed to choose at least one qubit more than once.
        num_non_unique_qubits = \
            random.randint(num_qubits + 1, 2 * (num_qubits + 1))
        non_unique_qubits = random.choices(qubits, k=num_non_unique_qubits)
        with pytest.raises(ValueError, match=expected_error):
            Instruction(non_unique_qubits, 'SOME_INSTRUCTION')



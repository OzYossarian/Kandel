import pytest
from pytest_mock import MockerFixture

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.Instruction import Instruction
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.PauliExtractor import PauliExtractor
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.UniformAncillaBasisExtractor import \
    UniformAncillaBasisExtractor


def test_uniform_ancilla_basis_extractor_auto_adds_pauli_I_extractor():
    ancilla_basis = PauliLetter('Z')
    pauli_extractors = {}
    extractor = UniformAncillaBasisExtractor(ancilla_basis, pauli_extractors)
    assert extractor.pauli_extractors[PauliLetter('I')] is None


def test_uniform_ancilla_basis_extractor_does_not_overwrite_pauli_I_extractor():
    ancilla_basis = PauliLetter('Z')
    identity_extractor = PauliExtractor(
        pre_rotations=['Some weird'],
        controlled_gate='way of',
        post_rotations=['doing nothing'],
        ancilla_is_control=True)
    pauli_extractors = {PauliLetter('I'): identity_extractor}
    extractor = UniformAncillaBasisExtractor(ancilla_basis, pauli_extractors)
    assert extractor.pauli_extractors[PauliLetter('I')] == identity_extractor


def test_uniform_ancilla_basis_extractor_get_ancilla_basis_fails_if_no_basis_given(mocker: MockerFixture):
    # Normally we wouldn't write a test for something that happens when an
    # argument of the wrong type is passed in (here we use None as the
    # parameter ancilla_basis of type PauliLetter). But because
    # PurePauliWordExtractor inherits from UniformAncillaBasisExtractor, and
    # just sets ancilla_basis to None, we ought to write a test for this.
    expected_error = \
        "Must tell the SyndromeExtractor the basis in which to initialise " \
        "and measure all ancillas"
    ancilla_basis = None
    pauli_extractors = {}
    extractor = UniformAncillaBasisExtractor(ancilla_basis, pauli_extractors)

    check = mocker.Mock(spec=Check)
    with pytest.raises(ValueError, match=expected_error):
        extractor.get_ancilla_basis(check)


def test_uniform_ancilla_basis_extractor_get_ancilla_basis_returns_correct_basis(mocker: MockerFixture):
    ancilla_basis = mocker.Mock(spec=PauliLetter)
    pauli_extractors = {}
    extractor = UniformAncillaBasisExtractor(ancilla_basis, pauli_extractors)

    check = mocker.Mock(spec=Check)
    result = extractor.get_ancilla_basis(check)
    assert result == ancilla_basis


def test_uniform_ancilla_basis_extractor_get_pre_rotations_fails_if_no_extractor(mocker: MockerFixture):
    expected_error = \
        "No data was given to the SyndromeExtractor specifying how to " \
        "extract pauli"
    ancilla_basis = mocker.Mock(spec=PauliLetter)
    pauli = mocker.Mock(spec=Pauli)
    pauli.letter = mocker.Mock(spec=PauliLetter)
    pauli_extractors = {}
    extractor = UniformAncillaBasisExtractor(ancilla_basis, pauli_extractors)

    check = mocker.Mock(spec=Check)
    with pytest.raises(ValueError, match=expected_error):
        extractor.get_pre_rotations(pauli, check)


def test_uniform_ancilla_basis_extractor_get_pre_rotations_returns_empty_list_if_extractor_is_none(
        mocker: MockerFixture):
    ancilla_basis = mocker.Mock(spec=PauliLetter)
    pauli = mocker.Mock(spec=Pauli)
    pauli.letter = mocker.Mock(spec=PauliLetter)
    pauli_extractors = {pauli.letter: None}
    extractor = UniformAncillaBasisExtractor(ancilla_basis, pauli_extractors)

    check = mocker.Mock(spec=Check)
    result = extractor.get_pre_rotations(pauli, check)
    assert result == []


def test_uniform_ancilla_basis_extractor_get_pre_rotations_returns_expected_instructions(mocker: MockerFixture):
    pauli = mocker.Mock(spec=Pauli)
    pauli.qubit = mocker.Mock(spec=Qubit)
    pauli.letter = mocker.Mock(spec=PauliLetter)

    pre_rotations = ['Pre', 'Rotate']
    pauli_extractor = mocker.Mock(spec=PauliExtractor)
    pauli_extractor.pre_rotations = pre_rotations

    pauli_extractors = {pauli.letter: pauli_extractor}
    ancilla_basis = mocker.Mock(spec=PauliLetter)
    extractor = UniformAncillaBasisExtractor(ancilla_basis, pauli_extractors)

    check = mocker.Mock(spec=Check)
    result = extractor.get_pre_rotations(pauli, check)
    assert len(result) == len(pre_rotations)
    for i in range(len(result)):
        instruction = result[i]
        assert instruction.qubits == [pauli.qubit]
        assert instruction.name == pre_rotations[i]



def test_uniform_ancilla_basis_extractor_get_post_rotations_fails_if_no_extractor(mocker: MockerFixture):
    expected_error = \
        "No data was given to the SyndromeExtractor specifying how to " \
        "extract pauli"
    ancilla_basis = mocker.Mock(spec=PauliLetter)
    pauli = mocker.Mock(spec=Pauli)
    pauli.letter = mocker.Mock(spec=PauliLetter)
    pauli_extractors = {}
    extractor = UniformAncillaBasisExtractor(ancilla_basis, pauli_extractors)

    check = mocker.Mock(spec=Check)
    with pytest.raises(ValueError, match=expected_error):
        extractor.get_post_rotations(pauli, check)


def test_uniform_ancilla_basis_extractor_get_post_rotations_returns_empty_list_if_extractor_is_none(
        mocker: MockerFixture):
    ancilla_basis = mocker.Mock(spec=PauliLetter)
    pauli = mocker.Mock(spec=Pauli)
    pauli.letter = mocker.Mock(spec=PauliLetter)
    pauli_extractors = {pauli.letter: None}
    extractor = UniformAncillaBasisExtractor(ancilla_basis, pauli_extractors)

    check = mocker.Mock(spec=Check)
    result = extractor.get_post_rotations(pauli, check)
    assert result == []


def test_uniform_ancilla_basis_extractor_get_post_rotations_returns_expected_instructions(mocker: MockerFixture):
    pauli = mocker.Mock(spec=Pauli)
    pauli.qubit = mocker.Mock(spec=Qubit)
    pauli.letter = mocker.Mock(spec=PauliLetter)

    post_rotations = ['Post', 'Rotate']
    pauli_extractor = mocker.Mock(spec=PauliExtractor)
    pauli_extractor.post_rotations = post_rotations

    pauli_extractors = {pauli.letter: pauli_extractor}
    ancilla_basis = mocker.Mock(spec=PauliLetter)
    extractor = UniformAncillaBasisExtractor(ancilla_basis, pauli_extractors)

    check = mocker.Mock(spec=Check)
    result = extractor.get_post_rotations(pauli, check)
    assert len(result) == len(post_rotations)
    for i in range(len(result)):
        instruction = result[i]
        assert instruction.qubits == [pauli.qubit]
        assert instruction.name == post_rotations[i]


def test_uniform_ancilla_basis_extractor_get_controlled_gate_fails_if_no_extractor(mocker: MockerFixture):
    expected_error = \
        "No data was given to the SyndromeExtractor specifying how to " \
        "extract pauli"
    ancilla_basis = mocker.Mock(spec=PauliLetter)
    pauli = mocker.Mock(spec=Pauli)
    pauli.letter = mocker.Mock(spec=PauliLetter)
    pauli_extractors = {}
    extractor = UniformAncillaBasisExtractor(ancilla_basis, pauli_extractors)

    check = mocker.Mock(spec=Check)
    with pytest.raises(ValueError, match=expected_error):
        extractor.get_controlled_gate(pauli, check)


def test_uniform_ancilla_basis_extractor_get_controlled_gate_returns_none_if_extractor_is_none(
        mocker: MockerFixture):
    ancilla_basis = mocker.Mock(spec=PauliLetter)
    pauli = mocker.Mock(spec=Pauli)
    pauli.letter = mocker.Mock(spec=PauliLetter)
    pauli_extractors = {pauli.letter: None}
    extractor = UniformAncillaBasisExtractor(ancilla_basis, pauli_extractors)

    check = mocker.Mock(spec=Check)
    result = extractor.get_controlled_gate(pauli, check)
    assert result is None


def test_uniform_ancilla_basis_extractor_get_controlled_gate_returns_expected_instruction_when_ancilla_is_control(
        mocker: MockerFixture):
    pauli = mocker.Mock(spec=Pauli)
    pauli.qubit = mocker.Mock(spec=Qubit)
    pauli.letter = mocker.Mock(spec=PauliLetter)

    controlled_gate = 'Controlled gate'
    pauli_extractor = mocker.Mock(spec=PauliExtractor)
    pauli_extractor.controlled_gate = controlled_gate
    pauli_extractor.ancilla_is_control = True

    pauli_extractors = {pauli.letter: pauli_extractor}
    ancilla_basis = mocker.Mock(spec=PauliLetter)
    extractor = UniformAncillaBasisExtractor(ancilla_basis, pauli_extractors)

    check = mocker.Mock(spec=Check)
    check.ancilla = mocker.Mock(spec=Qubit)
    result = extractor.get_controlled_gate(pauli, check)
    assert result.qubits == [check.ancilla, pauli.qubit]
    assert result.name == controlled_gate


def test_uniform_ancilla_basis_extractor_get_controlled_gate_returns_expected_instruction_when_ancilla_not_control(
        mocker: MockerFixture):
    pauli = mocker.Mock(spec=Pauli)
    pauli.qubit = mocker.Mock(spec=Qubit)
    pauli.letter = mocker.Mock(spec=PauliLetter)

    controlled_gate = 'Controlled gate'
    pauli_extractor = mocker.Mock(spec=PauliExtractor)
    pauli_extractor.controlled_gate = controlled_gate
    pauli_extractor.ancilla_is_control = False

    pauli_extractors = {pauli.letter: pauli_extractor}
    ancilla_basis = mocker.Mock(spec=PauliLetter)
    extractor = UniformAncillaBasisExtractor(ancilla_basis, pauli_extractors)

    check = mocker.Mock(spec=Check)
    check.ancilla = mocker.Mock(spec=Qubit)
    result = extractor.get_controlled_gate(pauli, check)
    assert result.qubits == [pauli.qubit, check.ancilla]
    assert result.name == controlled_gate

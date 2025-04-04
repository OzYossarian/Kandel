from main.compiling.syndrome_extraction.extractors.ancilla_per_check.PauliExtractor import PauliExtractor


def test_pauli_extractor_init():
    # Explicit example
    pre_rotations = ['S', 'S']
    controlled_gate = 'CNOT'
    ancilla_is_control = True
    post_rotations = ['S_DAGGER', 'S_DAGGER']
    extractor = PauliExtractor(
        pre_rotations, controlled_gate, ancilla_is_control, post_rotations)

    assert extractor.pre_rotations == pre_rotations
    assert extractor.controlled_gate == controlled_gate
    assert extractor.ancilla_is_control == ancilla_is_control
    assert extractor.post_rotations == post_rotations

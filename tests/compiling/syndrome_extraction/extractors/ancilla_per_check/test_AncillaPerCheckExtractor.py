import random

from pytest_mock import MockerFixture

from main.building_blocks.Check import Check
from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.Circuit import Circuit
from main.compiling.Instruction import Instruction
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import TrivialOrderer
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.AncillaPerCheckExtractor import \
    AncillaPerCheckExtractor
from main.utils.enums import State
from tests.utils.utils_numbers import default_test_repeats_small
from tests.utils.utils_strings import random_strings


def test_ancilla_per_check_extractor_defaults_to_trivial_extractor(mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate
    # an AncillaPerCheckExtractor
    mocker.patch.multiple(AncillaPerCheckExtractor, __abstractmethods__=set())
    extractor = AncillaPerCheckExtractor()
    assert isinstance(extractor.controlled_gate_orderer, TrivialOrderer)


def test_ancilla_per_check_extractor_overwrites_compiler_instructions(mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate
    # an AncillaPerCheckExtractor
    mocker.patch.multiple(AncillaPerCheckExtractor, __abstractmethods__=set())

    # Set up compiler and extarctor with different instructions
    extractor_initialisation_instructions = {
        State.Zero: ['R via Extractor']}
    extractor_measurement_instructions = {
        PauliLetter('Z'): ['M via Extractor']}
    compiler_initialisation_instructions = {
        State.Zero: ['R via Compiler']}
    compiler_measurement_instructions = {
        PauliLetter('Z'): ['M via Compiler']}
    extractor = AncillaPerCheckExtractor(
        initialisation_instructions=extractor_initialisation_instructions,
        measurement_instructions=extractor_measurement_instructions)
    compiler = AncillaPerCheckCompiler(
        initialisation_instructions=compiler_initialisation_instructions,
        measurement_instructions=compiler_measurement_instructions)
    circuit = Circuit()

    # Just set up one check with one Pauli
    check = mocker.Mock(spec=Check)
    check.paulis = {'0': mocker.Mock(spec=Pauli)}
    check.ancilla = mocker.Mock(spec=Qubit)

    # Mock over the inner methods.
    extractor.get_ancilla_basis = mocker.Mock(return_value=PauliLetter('Z'))
    compiler.initialize_qubits = mocker.Mock(return_value=0)
    extractor.extract_step = mocker.Mock(return_value=0)
    compiler.measure_individual_qubits = mocker.Mock(return_value=0)

    # Extract the checks
    extractor.extract_checks([check], 0, 0, circuit, compiler)

    # Assert that the right instructions were used.
    initial_states = {check.ancilla: State.Zero}
    compiler.initialize_qubits.assert_called_with(
        initial_states, 0, circuit, extractor_initialisation_instructions)
    final_paulis = [Pauli(check.ancilla, PauliLetter('Z'))]
    compiler.measure_individual_qubits.assert_called_with(
        final_paulis, [check], 0, 0, circuit, extractor_measurement_instructions)


def test_ancilla_per_check_extractor_defaults_to_compiler_instructions(mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate
    # an AncillaPerCheckExtractor
    mocker.patch.multiple(AncillaPerCheckExtractor, __abstractmethods__=set())

    # Don't pass in any specific extractor instructions.
    compiler_initialisation_instructions = {
        State.Zero: ['R via Compiler']}
    compiler_measurement_instructions = {
        PauliLetter('Z'): ['M via Compiler']}
    extractor = AncillaPerCheckExtractor()
    compiler = AncillaPerCheckCompiler(
        initialisation_instructions=compiler_initialisation_instructions,
        measurement_instructions=compiler_measurement_instructions)
    circuit = Circuit()

    # Just set up one check with one Pauli
    check = mocker.Mock(spec=Check)
    check.paulis = {'0': mocker.Mock(spec=Pauli)}
    check.ancilla = mocker.Mock(spec=Qubit)

    # Mock over the inner methods.
    extractor.get_ancilla_basis = mocker.Mock(return_value=PauliLetter('Z'))
    compiler.initialize_qubits = mocker.Mock(return_value=0)
    extractor.extract_step = mocker.Mock(return_value=0)
    compiler.measure_individual_qubits = mocker.Mock(return_value=0)

    # Extract the checks
    extractor.extract_checks([check], 0, 0, circuit, compiler)

    # Assert that the right instructions were used.
    initial_states = {check.ancilla: State.Zero}
    compiler.initialize_qubits.assert_called_with(
        initial_states, 0, circuit, compiler_initialisation_instructions)
    final_paulis = [Pauli(check.ancilla, PauliLetter('Z'))]
    compiler.measure_individual_qubits.assert_called_with(
        final_paulis, [check], 0, 0, circuit, compiler_measurement_instructions)


def test_ancilla_per_check_extractor_do_controlled_gate_when_pauli_none(mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate
    # AncillaPerCheckExtractor!
    mocker.patch.multiple(AncillaPerCheckExtractor, __abstractmethods__=set())
    extractor = AncillaPerCheckExtractor()

    # Set up the other data we need - we can use a mock Check to
    # make life easier for ourselves
    qubits = [Qubit(0), Qubit(1)]
    compiler = AncillaPerCheckCompiler()
    circuit = Circuit()
    pauli = None
    check = mocker.Mock(spec=Check)

    # Mock the return value of the get_controlled_gate function.
    mock_controlled_gate = Instruction(qubits, 'CONTROLLED_GATE')
    extractor.get_controlled_gate = \
        mocker.Mock(return_value=mock_controlled_gate)

    # Do the control gate
    extractor.do_controlled_gate(pauli, check, 0, circuit, compiler)

    # Assert nothing has happened because the Pauli was None.
    assert circuit.instructions == {}


def test_ancilla_per_check_extractor_do_controlled_gate_when_controlled_gate_none(mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate
    # AncillaPerCheckExtractor!
    mocker.patch.multiple(AncillaPerCheckExtractor, __abstractmethods__=set())
    extractor = AncillaPerCheckExtractor()

    # Set up the other data we need - we can use a mock Pauli and Check to
    # make life easier for ourselves
    compiler = AncillaPerCheckCompiler()
    circuit = Circuit()
    pauli = mocker.Mock(spec=Check)
    check = mocker.Mock(spec=Check)

    # Mock the return value of the get_controlled_gate function.
    mock_controlled_gate = None
    extractor.get_controlled_gate = \
        mocker.Mock(return_value=mock_controlled_gate)

    # Do the control gate
    extractor.do_controlled_gate(pauli, check, 0, circuit, compiler)

    # Assert nothing has happened because the Pauli was None.
    assert circuit.instructions == {}


def test_ancilla_per_check_extractor_do_controlled_gate_when_non_trivial(mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate
    # AncillaPerCheckExtractor!
    mocker.patch.multiple(AncillaPerCheckExtractor, __abstractmethods__=set())
    extractor = AncillaPerCheckExtractor()

    # Set up the other data we need - we can use a mock Pauli and Check to
    # make life easier for ourselves
    qubits = [Qubit(0), Qubit(1)]
    compiler = AncillaPerCheckCompiler()
    circuit = Circuit()
    pauli = mocker.Mock(spec=Pauli)
    check = mocker.Mock(spec=Check)

    # Mock the return value of the get_controlled_gate function.
    mock_controlled_gate = Instruction(qubits, 'CONTROLLED_GATE')
    extractor.get_controlled_gate = \
        mocker.Mock(return_value=mock_controlled_gate)

    # Do the control gate
    extractor.do_controlled_gate(pauli, check, 0, circuit, compiler)

    # Check that this has had the desired effect on the circuit
    expected = {
        0: {
            qubits[0]: [mock_controlled_gate],
            qubits[1]: [mock_controlled_gate]}}
    assert circuit.instructions == expected


def test_ancilla_per_check_extractor_pre_rotate_pauli_when_pauli_None(mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate
    # AncillaPerCheckExtractor!
    mocker.patch.multiple(AncillaPerCheckExtractor, __abstractmethods__=set())
    extractor = AncillaPerCheckExtractor()

    # Set up the other data we need - we can use a mock Pauli and Check to
    # make life easier for ourselves
    qubit = Qubit(0)
    compiler = AncillaPerCheckCompiler()
    circuit = Circuit()
    pauli = None
    check = mocker.Mock(spec=Check)

    # Mock the return value of the get_pre_rotations function.
    mock_pre_rotations = [
        Instruction([qubit], 'PRE_ROTATE_1'),
        Instruction([qubit], 'PRE_ROTATE_2')]
    extractor.get_pre_rotations = \
        mocker.Mock(return_value=mock_pre_rotations)

    # Pre-rotate!
    next_tick = extractor.pre_rotate_pauli(pauli, check, 0, circuit, compiler)

    # Check that nothing happened
    assert circuit.instructions == {}
    assert next_tick == 0


def test_ancilla_per_check_extractor_pre_rotate_pauli(mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate
    # AncillaPerCheckExtractor!
    mocker.patch.multiple(AncillaPerCheckExtractor, __abstractmethods__=set())
    extractor = AncillaPerCheckExtractor()

    # Set up the other data we need - we can use a mock Pauli and Check to
    # make life easier for ourselves
    qubit = Qubit(0)
    compiler = AncillaPerCheckCompiler()
    pauli = mocker.Mock(spec=Pauli)
    check = mocker.Mock(spec=Check)

    # Explicit test:
    mock_pre_rotations = [
        Instruction([qubit], 'PRE_ROTATE_1'),
        Instruction([qubit], 'PRE_ROTATE_2')]
    extractor.get_pre_rotations = \
        mocker.Mock(return_value=mock_pre_rotations)

    # Pre-rotate!
    circuit = Circuit()
    next_tick = extractor.pre_rotate_pauli(
        pauli, check, 0, circuit, compiler)

    # Check this has had the desired effect on the circuit
    expected = {
        0: {qubit: [mock_pre_rotations[0]]},
        2: {qubit: [mock_pre_rotations[1]]}}
    assert circuit.instructions == expected
    assert next_tick == 4

    # Random tests
    for _ in range(default_test_repeats_small):
        # Mock the return value of the get_pre_rotations function.
        num_pre_rotations = random.randint(0, 10)
        pre_rotation_names = random_strings(
            num_pre_rotations,
            max_length=10)
        mock_pre_rotations = [
            Instruction([qubit], name)
            for name in pre_rotation_names]
        extractor.get_pre_rotations = \
            mocker.Mock(return_value=mock_pre_rotations)

        # Pre-rotate!
        circuit = Circuit()
        next_tick = extractor.pre_rotate_pauli(
            pauli, check, 0, circuit, compiler)

        # Check this has had the desired effect on the circuit
        expected = {
            2*i: {qubit: [mock_pre_rotations[i]]}
            for i in range(num_pre_rotations)}
        assert circuit.instructions == expected
        assert next_tick == 2 * num_pre_rotations


def test_ancilla_per_check_extractor_post_rotate_pauli_when_pauli_None(mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate
    # an AncillaPerCheckExtractor
    mocker.patch.multiple(AncillaPerCheckExtractor, __abstractmethods__=set())
    extractor = AncillaPerCheckExtractor()

    # Set up the other data we need - we can use a mock Pauli and Check to
    # make life easier for ourselves
    qubit = Qubit(0)
    compiler = AncillaPerCheckCompiler()
    circuit = Circuit()
    pauli = None
    check = mocker.Mock(spec=Check)

    # Mock the return value of the get_pre_rotations function.
    mock_post_rotations = [
        Instruction([qubit], 'POST_ROTATE_1'),
        Instruction([qubit], 'POST_ROTATE_2')]
    extractor.get_post_rotations = \
        mocker.Mock(return_value=mock_post_rotations)

    # Pre-rotate!
    next_tick = extractor.post_rotate_pauli(pauli, check, 0, circuit, compiler)

    # Check that nothing happened
    assert circuit.instructions == {}
    assert next_tick == 0


def test_ancilla_per_check_extractor_post_rotate_pauli(mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate
    # an AncillaPerCheckExtractor
    mocker.patch.multiple(AncillaPerCheckExtractor, __abstractmethods__=set())
    extractor = AncillaPerCheckExtractor()

    # Set up the other data we need - we can use a mock Pauli and Check to
    # make life easier for ourselves
    qubit = Qubit(0)
    compiler = AncillaPerCheckCompiler()
    pauli = mocker.Mock(spec=Pauli)
    check = mocker.Mock(spec=Check)

    # Explicit test:
    mock_post_rotations = [
        Instruction([qubit], 'POST_ROTATE_1'),
        Instruction([qubit], 'POST_ROTATE_2')]
    extractor.get_post_rotations = \
        mocker.Mock(return_value=mock_post_rotations)

    # Pre-rotate!
    circuit = Circuit()
    next_tick = extractor.post_rotate_pauli(
        pauli, check, 0, circuit, compiler)

    # Check this has had the desired effect on the circuit
    expected = {
        0: {qubit: [mock_post_rotations[0]]},
        2: {qubit: [mock_post_rotations[1]]}}
    assert circuit.instructions == expected
    assert next_tick == 4

    # Random tests
    for _ in range(default_test_repeats_small):
        # Mock the return value of the get_post_rotations function.
        num_post_rotations = random.randint(0, 10)
        post_rotation_names = random_strings(
            num_post_rotations,
            max_length=10)
        mock_post_rotations = [
            Instruction([qubit], name)
            for name in post_rotation_names]
        extractor.get_post_rotations = \
            mocker.Mock(return_value=mock_post_rotations)

        # Pre-rotate!
        circuit = Circuit()
        next_tick = extractor.post_rotate_pauli(
            pauli, check, 0, circuit, compiler)

        # Check this has had the desired effect on the circuit
        expected = {
            2*i: {qubit: [mock_post_rotations[i]]}
            for i in range(num_post_rotations)}
        assert circuit.instructions == expected
        assert next_tick == 2 * num_post_rotations


def test_ancilla_per_check_extractor_extract_step(mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate
    # an AncillaPerCheckExtractor
    mocker.patch.multiple(AncillaPerCheckExtractor, __abstractmethods__=set())
    extractor = AncillaPerCheckExtractor()
    compiler = AncillaPerCheckCompiler()
    circuit = Circuit()

    # Mock up two weight-two checks, with a length-3 extraction circuit
    checks = [
        mocker.Mock(spec=Check),
        mocker.Mock(spec=Check)]
    ordered_paulis = [
        [mocker.Mock(spec=Pauli), mocker.Mock(spec=Pauli), None],
        [None, mocker.Mock(spec=Pauli), mocker.Mock(spec=Pauli)]]

    # Mock up the pre-rotations, post-rotations and controlled gates.
    def mock_pre_rotate_pauli(pauli, check, tick, circuit, compiler):
        return tick + 1

    def mock_do_controlled_gate(pauli, check, tick, circuit, compiler):
        # Irrelevant what we return here - a controlled gate always takes
        # two ticks.
        return None

    def mock_post_rotate_pauli(pauli, check, tick, circuit, compiler):
        return tick + 3

    extractor.pre_rotate_pauli = \
        mocker.Mock(side_effect=mock_pre_rotate_pauli)
    extractor.do_controlled_gate = \
        mocker.Mock(side_effect=mock_do_controlled_gate)
    extractor.post_rotate_pauli = \
        mocker.Mock(side_effect=mock_post_rotate_pauli)

    # Extract step 0
    tick = 0
    next_tick = extractor.extract_step(
        0, checks, ordered_paulis, tick, circuit, compiler)

    # Assert that the expected calls to the inner functions were made.
    # Since these inner functions are tested separately, this suffices to
    # test that this method here works. (The alternative of actually
    # checking the right circuit is created is a lot more fiddly and
    # depends on too many other functions).
    expected_pre_rotate_calls = [
        mocker.call(ordered_paulis[0][0], checks[0], 0, circuit, compiler),
        mocker.call(ordered_paulis[1][0], checks[1], 0, circuit, compiler)]
    extractor.pre_rotate_pauli.assert_has_calls(
        expected_pre_rotate_calls, any_order=True)

    expected_do_controlled_gate_calls = [
        mocker.call(ordered_paulis[0][0], checks[0], 1, circuit, compiler),
        mocker.call(ordered_paulis[1][0], checks[1], 1, circuit, compiler)]
    extractor.do_controlled_gate.assert_has_calls(
        expected_do_controlled_gate_calls, any_order=True)

    expected_post_rotate_calls = [
        mocker.call(ordered_paulis[0][0], checks[0], 3, circuit, compiler),
        mocker.call(ordered_paulis[1][0], checks[1], 3, circuit, compiler)]
    extractor.post_rotate_pauli.assert_has_calls(
        expected_post_rotate_calls, any_order=True)

    assert next_tick == 6
    tick = next_tick

    # Extract step 1
    next_tick = extractor.extract_step(
        1, checks, ordered_paulis, tick, circuit, compiler)

    expected_pre_rotate_calls = [
        mocker.call(ordered_paulis[0][1], checks[0], 6, circuit, compiler),
        mocker.call(ordered_paulis[1][1], checks[1], 6, circuit, compiler)]
    extractor.pre_rotate_pauli.assert_has_calls(
        expected_pre_rotate_calls, any_order=True)

    expected_do_controlled_gate_calls = [
        mocker.call(ordered_paulis[0][1], checks[0], 7, circuit, compiler),
        mocker.call(ordered_paulis[1][1], checks[1], 7, circuit, compiler)]
    extractor.do_controlled_gate.assert_has_calls(
        expected_do_controlled_gate_calls, any_order=True)

    expected_post_rotate_calls = [
        mocker.call(ordered_paulis[0][1], checks[0], 9, circuit, compiler),
        mocker.call(ordered_paulis[1][1], checks[1], 9, circuit, compiler)]
    extractor.post_rotate_pauli.assert_has_calls(
        expected_post_rotate_calls, any_order=True)

    assert next_tick == 12
    tick = next_tick

    # Extract step 2
    next_tick = extractor.extract_step(
        2, checks, ordered_paulis, tick, circuit, compiler)

    expected_pre_rotate_calls = [
        mocker.call(ordered_paulis[0][2], checks[0], 12, circuit, compiler),
        mocker.call(ordered_paulis[1][2], checks[1], 12, circuit, compiler)]
    extractor.pre_rotate_pauli.assert_has_calls(
        expected_pre_rotate_calls, any_order=True)

    expected_do_controlled_gate_calls = [
        mocker.call(ordered_paulis[0][2], checks[0], 13, circuit, compiler),
        mocker.call(ordered_paulis[1][2], checks[1], 13, circuit, compiler)]
    extractor.do_controlled_gate.assert_has_calls(
        expected_do_controlled_gate_calls, any_order=True)

    expected_post_rotate_calls = [
        mocker.call(ordered_paulis[0][2], checks[0], 15, circuit, compiler),
        mocker.call(ordered_paulis[1][2], checks[1], 15, circuit, compiler)]
    extractor.post_rotate_pauli.assert_has_calls(
        expected_post_rotate_calls, any_order=True)

    assert next_tick == 18


def test_ancilla_per_check_extractor_extract_checks_in_parallel(mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate
    # an AncillaPerCheckExtractor
    mocker.patch.multiple(AncillaPerCheckExtractor, __abstractmethods__=set())
    initialisation_instructions = {
        State.Zero: ['INITIALIZE_0_STATE']}
    measurement_instructions = {
        PauliLetter('Z'): ['MEASURE_Z']}
    extractor = AncillaPerCheckExtractor(
        initialisation_instructions=initialisation_instructions,
        measurement_instructions=measurement_instructions,
        parallelize=True)
    compiler = AncillaPerCheckCompiler()
    circuit = Circuit()

    # Mock over the key inner methods. To check this method itself works,
    # we'll just assert that the inner methods were called with the right
    # arguments. Since these inner methods are tested, this suffices.
    extractor.get_ancilla_basis = mocker.Mock(return_value=PauliLetter('Z'))
    compiler.initialize_qubits = mocker.Mock(
        side_effect=lambda _, tick, __, ___: tick + 2)
    extractor.extract_step = mocker.Mock(
        side_effect=lambda _, __, ___, tick, ____, _____: tick + 10)
    compiler.measure_individual_qubits = mocker.Mock(
        side_effect=lambda _, __, ___, tick, ____, _____: tick + 4)

    # Mock up two weight-2 checks
    paulis = [
        [mocker.Mock(spec=Pauli), mocker.Mock(spec=Pauli)],
        [mocker.Mock(spec=Pauli), mocker.Mock(spec=Pauli)]]
    checks = [
        mocker.Mock(spec=Check),
        mocker.Mock(spec=Check)]
    # Set checks' paulis and ancillas
    checks[0].paulis = {i: paulis[0][i] for i in range(2)}
    checks[1].paulis = {i: paulis[1][i] for i in range(2)}
    checks[0].ancilla = mocker.Mock(spec=Qubit)
    checks[1].ancilla = mocker.Mock(spec=Qubit)

    round = 0
    next_tick = extractor.extract_checks(checks, round, 0, circuit, compiler)

    # Check ancillas were initialised
    initial_states = {
        checks[0].ancilla: State.Zero,
        checks[1].ancilla: State.Zero}
    compiler.initialize_qubits.assert_called_with(
        initial_states, 0, circuit, initialisation_instructions)

    # Check all the Paulis in the checks were extracted
    expected_extract_step_calls = [
        mocker.call(0, checks, paulis, 2, circuit, compiler),
        mocker.call(1, checks, paulis, 12, circuit, compiler)]
    extractor.extract_step.assert_has_calls(
        expected_extract_step_calls)

    # Check ancillas were measured.
    paulis = [
        Pauli(checks[0].ancilla, PauliLetter('Z')),
        Pauli(checks[1].ancilla, PauliLetter('Z'))]
    compiler.measure_individual_qubits.assert_called_with(
        paulis, checks, round, 22, circuit, measurement_instructions)

    assert next_tick == 26


def test_ancilla_per_check_extractor_extract_checks_in_sequence(mocker: MockerFixture):
    # Patch over the abstract methods so that we can instantiate
    # an AncillaPerCheckExtractor
    mocker.patch.multiple(AncillaPerCheckExtractor, __abstractmethods__=set())
    initialisation_instructions = {
        State.Zero: ['INITIALIZE_0_STATE']}
    measurement_instructions = {
        PauliLetter('Z'): ['MEASURE_Z']}
    extractor = AncillaPerCheckExtractor(
        initialisation_instructions=initialisation_instructions,
        measurement_instructions=measurement_instructions,
        parallelize=False)
    compiler = AncillaPerCheckCompiler()
    circuit = Circuit()

    # Mock over the key inner methods. To check this method itself works,
    # we'll just assert that the inner methods were called with the right
    # arguments. Since these inner methods are tested, this suffices.
    extractor.get_ancilla_basis = mocker.Mock(return_value=PauliLetter('Z'))
    compiler.initialize_qubits = mocker.Mock(
        side_effect=lambda _, tick, __, ___: tick + 2)
    extractor.extract_step = mocker.Mock(
        side_effect=lambda _, __, ___, tick, ____, _____: tick + 10)
    compiler.measure_individual_qubits = mocker.Mock(
        side_effect=lambda _, __, ___, tick, ____, _____: tick + 4)

    # Mock up two weight-2 checks
    paulis = [
        [mocker.Mock(spec=Pauli), mocker.Mock(spec=Pauli)],
        [mocker.Mock(spec=Pauli), mocker.Mock(spec=Pauli)]]
    checks = [
        mocker.Mock(spec=Check),
        mocker.Mock(spec=Check)]
    # Set checks' paulis and ancillas
    checks[0].paulis = {i: paulis[0][i] for i in range(2)}
    checks[1].paulis = {i: paulis[1][i] for i in range(2)}
    checks[0].ancilla = mocker.Mock(spec=Qubit)
    checks[1].ancilla = mocker.Mock(spec=Qubit)

    round = 0
    next_tick = extractor.extract_checks(checks, round, 0, circuit, compiler)

    # Check ancillas were initialised
    expected_initialise_qubits_calls = [
        mocker.call({checks[0].ancilla: State.Zero}, 0, circuit, initialisation_instructions),
        mocker.call({checks[1].ancilla: State.Zero}, 26, circuit, initialisation_instructions)]
    compiler.initialize_qubits.assert_has_calls(
        expected_initialise_qubits_calls, any_order=True)

    # Check all the Paulis in the checks were extracted
    expected_extract_step_calls = [
        mocker.call(0, checks[:1], paulis[:1], 2, circuit, compiler),
        mocker.call(1, checks[:1], paulis[:1], 12, circuit, compiler),
        mocker.call(0, checks[1:], paulis[1:], 28, circuit, compiler),
        mocker.call(1, checks[1:], paulis[1:], 38, circuit, compiler)]
    extractor.extract_step.assert_has_calls(
        expected_extract_step_calls)

    # Check ancillas were measured.
    measurement_paulis = [
        Pauli(checks[0].ancilla, PauliLetter('Z')),
        Pauli(checks[1].ancilla, PauliLetter('Z'))]
    expected_measure_qubits_calls = [
        mocker.call(measurement_paulis[:1], checks[:1], round, 22, circuit, measurement_instructions),
        mocker.call(measurement_paulis[1:], checks[1:], round, 48, circuit, measurement_instructions)]
    compiler.measure_individual_qubits.assert_has_calls(
        expected_measure_qubits_calls, any_order=True)

    assert next_tick == 52

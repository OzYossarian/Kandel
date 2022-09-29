from main.building_blocks.Qubit import Qubit
from main.compiling.noise.noises import OneQubitNoise
from tests.compiling.noise.utils_noise import MockNoise


def test_noise_unequal_if_types_differ():
    one_qubit_noise = OneQubitNoise(0.1, 0.1, 0.1)
    mock_noise = MockNoise(one_qubit_noise.name, (0.1, 0.1, 0.1))
    assert mock_noise != one_qubit_noise


def test_noise_unequal_if_names_differ():
    mock_noise_1 = MockNoise('MOCK_NOISE_1', (0.1, 0.1))
    mock_noise_2 = MockNoise('MOCK_NOISE_2', (0.1, 0.1))
    assert mock_noise_1 != mock_noise_2


def test_noise_unequal_if_params_differ():
    mock_noise_1 = MockNoise('MOCK_NOISE', (0.1, 0.1))
    mock_noise_2 = MockNoise('MOCK_NOISE', (0.2, 0.2))
    assert mock_noise_1 != mock_noise_2


def test_noise_equal_when_expected():
    mock_noise_1 = MockNoise('MOCK_NOISE', (0.1, 0.1))
    mock_noise_2 = MockNoise('MOCK_NOISE', (0.1, 0.1))
    assert mock_noise_1 == mock_noise_2


def test_noise_instruction():
    # Explicit test:
    name = 'MOCK_NOISE'
    params = (0.1, 0.2, 0.3)
    noise = MockNoise(name, params)
    qubits = [Qubit(0), Qubit(1)]
    instruction = noise.instruction(qubits)

    assert instruction.qubits == qubits
    assert instruction.name == name
    assert instruction.params == params
    assert instruction.is_noise




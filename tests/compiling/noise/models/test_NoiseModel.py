from main.compiling.noise.models.NoiseModel import NoiseModel
from tests.compiling.noise.utils_noise import MockNoise


def test_noise_model_default_to_uniform_noise_arg_is_none():
    arg = None
    result = NoiseModel.default_to_uniform_noise(arg, MockNoise)
    expected = None
    assert result == expected


def test_noise_model_default_to_uniform_noise_arg_is_float():
    arg = 0.1
    result = NoiseModel.default_to_uniform_noise(arg, MockNoise)
    expected = MockNoise('MOCK_NOISE', arg)
    assert result == expected


def test_noise_model_default_to_uniform_noise_arg_is_int():
    arg = 1
    result = NoiseModel.default_to_uniform_noise(arg, MockNoise)
    expected = MockNoise('MOCK_NOISE', arg)
    assert result == expected


def test_noise_model_default_to_uniform_noise_arg_is_noise():
    arg = MockNoise('MOCK_NOISE', 0.1)
    result = NoiseModel.default_to_uniform_noise(arg, MockNoise)
    expected = arg
    assert result == expected


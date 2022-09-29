import random

from main.compiling.noise.noises import OneBitNoise


def test_one_bit_noise_uniform():
    p = random.uniform(0, 1)
    expected = OneBitNoise(p)
    assert OneBitNoise.uniform(p) == expected


def test_one_bit_noise_name():
    p = random.uniform(0, 1)
    noise = OneBitNoise(p)
    assert noise.name is None


def test_one_bit_noise_params():
    p = random.uniform(0, 1)
    noise = OneBitNoise(p)
    assert noise.params == p

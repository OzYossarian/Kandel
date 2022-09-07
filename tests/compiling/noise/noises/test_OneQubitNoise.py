import random

import numpy as np

from main.compiling.noise.noises import OneQubitNoise


def test_one_qubit_noise_uniform():
    p = random.uniform(0, 1)
    q = p/3
    expected = OneQubitNoise(q, q, q)
    assert OneQubitNoise.uniform(p) == expected


def test_one_qubit_noise_name():
    [px, py, pz] = np.random.uniform(0, 1, size=3)
    noise = OneQubitNoise(px, py, pz)
    assert noise.name == 'PAULI_CHANNEL_1'


def test_one_qubit_noise_params():
    [px, py, pz] = np.random.uniform(0, 1, size=3)
    noise = OneQubitNoise(px, py, pz)
    assert noise.params == (px, py, pz)

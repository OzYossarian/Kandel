import random

import numpy as np

from main.compiling.noise.noises import TwoQubitNoise


def test_two_qubit_noise_uniform():
    p = random.uniform(0, 1)
    q = p/15
    expected = TwoQubitNoise(q, q, q, q, q, q, q, q, q, q, q, q, q, q, q)
    assert TwoQubitNoise.uniform(p) == expected


def test_two_qubit_noise_name():
    [pix, piy, piz, pxi, pxx, pxy, pxz, pyi, pyx, pyy, pyz, pzi, pzx, pzy, pzz] = \
        np.random.uniform(0, 1, size=15)
    noise = TwoQubitNoise(
        pix, piy, piz, pxi, pxx, pxy, pxz, pyi, pyx, pyy, pyz, pzi, pzx, pzy, pzz)
    assert noise.name == 'PAULI_CHANNEL_2'


def test_two_qubit_noise_params():
    [pix, piy, piz, pxi, pxx, pxy, pxz, pyi, pyx, pyy, pyz, pzi, pzx, pzy, pzz] = \
        np.random.uniform(0, 1, size=15)
    noise = TwoQubitNoise(
        pix, piy, piz, pxi, pxx, pxy, pxz, pyi, pyx, pyy, pyz, pzi, pzx, pzy, pzz)
    assert noise.params == \
           (pix, piy, piz, pxi, pxx, pxy, pxz, pyi, pyx, pyy, pyz, pzi, pzx, pzy, pzz)
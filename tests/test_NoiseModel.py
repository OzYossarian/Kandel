import math
from main.compiling.noise.models import (
    CircuitLevelNoise,
    CodeCapacityBitFlipNoise,
    PhenomenologicalNoise,
)
from main.compiling.noise.noises import OneQubitNoise, TwoQubitNoise


def test_init_code_capacity_bit_flip_noise():
    noise_model = CodeCapacityBitFlipNoise(0.2)
    assert noise_model.data_qubit_start_round.px == 0.2
    assert noise_model.data_qubit_start_round.py == 0
    assert noise_model.data_qubit_start_round.pz == 0


def test_init_phenomenological_noise():
    noise_model = PhenomenologicalNoise(0.15, 0.1)
    assert math.isclose(noise_model.data_qubit_start_round.px, 0.05, rel_tol=1e-5)
    assert math.isclose(noise_model.data_qubit_start_round.py, 0.05, rel_tol=1e-5)
    assert math.isclose(noise_model.data_qubit_start_round.pz, 0.05, rel_tol=1e-5)
    assert math.isclose(noise_model.measurement.p, 0.1)


def test_init_circuit_level_noise():
    noise_model = CircuitLevelNoise(
        initialisation=0.17,
        idling=0.15,
        two_qubit_gate=0.2,
        one_qubit_gate=0.15,
        measurement=0.1,
    )

    assert noise_model.initialisation.px == ["X_Error", 0.17]
    assert noise_model.initialisation.py == ["X_Error", 0.17]
    assert noise_model.initialisation.pz == ["X_Error", 0.17]


    assert noise_model.measurement == ["X_Error", 0.17]
    assert noise_model.measurement == ["X_Error", 0.1]
    assert noise_model.one_qubit_gate == ["DEPOLARIZE1", 0.15]
    assert noise_model.two_qubit_gate == ["DEPOLARIZE2", 0.2]

import math

from main.compiling.noise.models import CircuitLevelNoise


def test_init_circuit_level_noise():
    noise_model = CircuitLevelNoise(
        initialisation=0.17,
        idling=0.15,
        two_qubit_gate=0.2,
        one_qubit_gate=0.15,
        measurement=0.1,
    )

    assert math.isclose(noise_model.initialisation.px, 1 / 3 * 0.17, rel_tol=1e-5)
    assert math.isclose(noise_model.initialisation.py, 1 / 3 * 0.17, rel_tol=1e-5)
    assert math.isclose(noise_model.initialisation.pz, 1 / 3 * 0.17, rel_tol=1e-5)

    assert noise_model.measurement.p == 0.1
    assert math.isclose(noise_model.one_qubit_gate.px, 0.15 / 3, rel_tol=1e-5)
    assert math.isclose(noise_model.one_qubit_gate.py, 0.15 / 3, rel_tol=1e-5)
    assert math.isclose(noise_model.one_qubit_gate.pz, 0.15 / 3, rel_tol=1e-5)

    for prob in noise_model.two_qubit_gate.__dict__:
        assert math.isclose(
            noise_model.two_qubit_gate.__dict__[prob], 0.2 / 15, rel_tol=1e-5
        )

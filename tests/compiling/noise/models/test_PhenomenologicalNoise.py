import math

from main.compiling.noise.models import PhenomenologicalNoise


def test_init_phenomenological_noise():
    noise_model = PhenomenologicalNoise(0.15, 0.1)
    assert math.isclose(noise_model.data_qubit_start_round.px, 0.05, rel_tol=1e-5)
    assert math.isclose(noise_model.data_qubit_start_round.py, 0.05, rel_tol=1e-5)
    assert math.isclose(noise_model.data_qubit_start_round.pz, 0.05, rel_tol=1e-5)
    assert math.isclose(noise_model.measurement.p, 0.1)
from main.compiling.noise.models import CodeCapacityBitFlipNoise


def test_init_code_capacity_bit_flip_noise():
    noise_model = CodeCapacityBitFlipNoise(0.2)
    assert noise_model.data_qubit_start_round.px == 0.2
    assert noise_model.data_qubit_start_round.py == 0
    assert noise_model.data_qubit_start_round.pz == 0

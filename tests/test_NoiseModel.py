from main.NoiseModel import CircuitLevelNoise, CodeCapactiyBitFlipNoise, PhenomenologicalNoise


def test_init_code_capacity_bit_flip_noise():
    noise_model = CodeCapactiyBitFlipNoise(0.2)
    assert noise_model.data_qubit_RZ == ['X_Error', 0.2]


def test_init_phenomenological_noise():
    noise_model = PhenomenologicalNoise(0.15, 0.1)
    assert noise_model.data_qubit_start_round == ['DEPOLARIZE1', 0.15]
    assert noise_model.ancilla_qubit_MZ == ['X_Error', 0.1]


def test_init_circuit_level_noise():
    noise_model = CircuitLevelNoise(0.15, p_sp=0.17, p_2=0.2, p_m=0.1)
    assert noise_model.data_qubit_RZ == ['X_Error', 0.17]
    assert noise_model.ancilla_qubit_RZ == ['X_Error', 0.17]
    assert noise_model.ancilla_qubit_MZ == ['X_Error', 0.1]
    assert noise_model.single_qubit_gate == ['DEPOLARIZE1', 0.15]
    assert noise_model.two_qubit_gate == ['DEPOLARIZE2', 0.2]

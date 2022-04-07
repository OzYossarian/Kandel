class NoiseModel(object):
    def __init__(self, noise_settings):
        default_input = {
            'data_qubit_RZ': 0,
            'ancilla_qubit_RZ': 0,
            'ancilla_qubit_MZ': 0,
            'single_qubit_gate': 0,
            'two_qubit_gate': 0,
            'data_qubit_start_round': 0
        }
        for key in noise_settings.keys():
            self.__dict__[key] = noise_settings[key]
        for key in default_input.keys():
            if key not in noise_settings:
                self.__dict__[key] = default_input[key]


class CodeCapactiyBitFlipNoise(NoiseModel):
    def __init__(self, bit_flip_probability):
        super().__init__({'data_qubit_RZ': ['X_Error', bit_flip_probability]})


class PhenomenologicalNoise(NoiseModel):
    def __init__(self, data_qubit_p1, measurement_noise):
        super().__init__(
            {'data_qubit_start_round': ['DEPOLARIZE1', data_qubit_p1],
             'ancilla_qubit_MZ': ['X_Error', measurement_noise]})


class CircuitLevelNoise():
    def __init__(self, bit_flip_probability):
        pass

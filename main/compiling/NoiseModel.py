from typing import Dict


class NoiseModel(object):
    def __init__(self, noise_settings=None):
        """Parent class for generating a noise model

        Args:
            noise_settings (Dict, optional):
                Keys are the type of noise and the values are the probability
                that this type of noise occurs. See CodeCapacityBitFlipNoise,
                PhenomenologicalNoise and CircuitLevelNoise for examples.
                Defaults to dict().
        """

        if noise_settings is None:
            noise_settings = dict()

        default_input = {
            'data_qubit_RZ': 0,
            'ancilla_qubit_RZ': 0,
            'ancilla_qubit_MZ': 0,
            'data_qubit_MZ': 0,
            'single_qubit_gate': 0,
            'two_qubit_gate': 0,
            'data_qubit_start_round': 0,
            'idling_noise': 0,
        }
        for key in noise_settings.keys():
            self.__dict__[key] = noise_settings[key]
        for key in default_input.keys():
            if key not in noise_settings:
                self.__dict__[key] = default_input[key]


class CodeCapactiyBitFlipNoise(NoiseModel):
    def __init__(self, bit_flip_probability: float):
        """Creates a code capacity bit flip (X error) noise model

        Intended for simulations where all stabilizers are measured once

        Args:
            bit_flip_probability (float): probability of a bit flip error
                                          occuring on a data qubit
        """
        super().__init__({'data_qubit_RZ': ['X_Error', bit_flip_probability]})


class PhenomenologicalNoise(NoiseModel):
    def __init__(self, data_qubit_p1: float, measurement_noise: float):
        """Creates a phenomenological noise model

        Args:
            data_qubit_p1 (float): probability of inserting an X,Y or Z
                                   error on data qubits in between measurement
                                   rounds
            measurement_noise (float): probability of inserting a bit flip
                                       error before measuring an ancilla qubit
        """
        super().__init__(
            {'data_qubit_start_round': ['DEPOLARIZE1', data_qubit_p1],
             'ancilla_qubit_MZ': ['X_Error', measurement_noise]})


class CircuitLevelNoise(NoiseModel):
    def __init__(self, p_1: float, p_sp: float, p_2: float, p_m: float):
        """Create a circuit level noise model

        Args:
            p1 (float): probability of inserting an X, Y or  Z error after
                        a single qubit gate or an idling location
            p_sp (float): probability of inserting a bit flip error after
                          state preperation
            p_2 (float): probability of inserting an element from the two qubit
                         Pauli group after a two qubit gate
            p_m (float): probability of inserting a bit flip error before
                         measurement
        """
        super().__init__(
            {'data_qubit_RZ': ['X_Error', p_sp],
             'ancilla_qubit_RZ': ['X_Error', p_sp],
             'ancilla_qubit_MZ': ['X_Error', p_m],
             'data_qubit_MZ': ['X_Error', p_m],
             'single_qubit_gate': ['DEPOLARIZE1', p_1],
             'idling_noise': ['DEPOLARIZE1', p_1],
             'two_qubit_gate': ['DEPOLARIZE2', p_2]}
        )

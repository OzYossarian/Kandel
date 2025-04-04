from main.compiling.noise.models.NoiseModel import NoiseModel


class StandardDepolarizingNoise(NoiseModel):
    def __init__(self, p: float):
        super().__init__(
            # 3/2 such that the sum of the two errors that act non trivially is 1.
            initialisation=3/2*p,
            idling=p,
            one_qubit_gate=p,
            two_qubit_gate=p,
            measurement=p,
        )

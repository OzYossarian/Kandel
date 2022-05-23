from main.compiling.noise.Noise import Noise


class OneQubitNoise(Noise):
    def __init__(self, px: float = 0, py: float = 0, pz: float = 0):
        super().__init__()
        self.px = px
        self.py = py
        self.pz = pz

    @classmethod
    def uniform(cls, p: float):
        q = p / 3
        return cls(q, q, q)

    @property
    def name(self):
        return 'PAULI_CHANNEL_1'

    @property
    def params(self):
        return self.px, self.py, self.pz

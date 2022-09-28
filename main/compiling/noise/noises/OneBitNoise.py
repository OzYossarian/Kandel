from main.compiling.noise.noises.Noise import Noise


class OneBitNoise(Noise):
    def __init__(self, p):
        super().__init__()
        self.p = p

    @classmethod
    def uniform(cls, p: float):
        return cls(p)

    @property
    def name(self):
        # Stim has no one-bit noise channel.
        # Instead, this class should be used to parametrise Stim
        # instructions, like measurements.
        return None

    @property
    def params(self):
        return self.p

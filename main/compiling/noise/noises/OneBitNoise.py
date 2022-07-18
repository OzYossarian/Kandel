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
        # Note - this isn't a noise name that is recognised by Stim
        raise ValueError

    @property
    def params(self):
        return self.p

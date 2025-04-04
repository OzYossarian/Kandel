from main.compiling.noise.models.NoiseModel import NoiseModel


class EM3(NoiseModel):

    def __init__(
            self,
            p: float):
        super().__init__(
            initialisation=3/2*p,
            idling=p,
            measurement=p,
            before_mpp_noise=p,
        )

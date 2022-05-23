from main.compiling.noise.noises.Noise import Noise


class TwoQubitNoise(Noise):
    def __init__(
            self,
            pix: float = 0,
            piy: float = 0,
            piz: float = 0,
            pxi: float = 0,
            pxx: float = 0,
            pxy: float = 0,
            pxz: float = 0,
            pyi: float = 0,
            pyx: float = 0,
            pyy: float = 0,
            pyz: float = 0,
            pzi: float = 0,
            pzx: float = 0,
            pzy: float = 0,
            pzz: float = 0):
        super().__init__()
        self.pix = pix
        self.piy = piy
        self.piz = piz
        self.pxi = pxi
        self.pxx = pxx
        self.pxy = pxy
        self.pxz = pxz
        self.pyi = pyi
        self.pyx = pyx
        self.pyy = pyy
        self.pyz = pyz
        self.pzi = pzi
        self.pzx = pzx
        self.pzy = pzy
        self.pzz = pzz

    @classmethod
    def uniform(cls, p: float):
        q = p / 15
        return cls(q, q, q, q, q, q, q, q, q, q, q, q, q, q, q)

    @property
    def name(self):
        return 'PAULI_CHANNEL_2'

    @property
    def params(self):
        return (
            self.pix,
            self.piy,
            self.piz,
            self.pxi,
            self.pxx,
            self.pxy,
            self.pxz,
            self.pyi,
            self.pyx,
            self.pyy,
            self.pyz,
            self.pzi,
            self.pzx,
            self.pzy,
            self.pzz)

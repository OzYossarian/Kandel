from typing import Tuple

from main.codes.Code import Code


class ToricCode(Code):
    """
    An unfortunate name clash! This is not "the" toric code, but
    rather a base class for any code with a toric geometry. e.g. One can
    define a toric colour code or a toric tic-tac-toe code.
    """
    def __init__(self, width: int, height: int, **kwargs):
        """
        Args:
            width: width of the torus on which this code lives
            height: height of the torus on which this code lives
        """
        self.width = width
        self.height = height
        super().__init__(**kwargs)

    def wrap_coords(self, coords: Tuple[int, int]):
        """Returns coordinates modulo the torus' width and height.
        """
        (x, y) = coords
        wrapped = (x % self.width, y % self.height)
        return wrapped

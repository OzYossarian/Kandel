from main.codes.Code import Code
from main.utils.Colour import Blue, Green, Red


class ThreeColourableCode(Code):
    """
    Many codes can be defined on any three-colourable lattice -
    e.g. colour code, tic-tac-toe codes. This is a base class for
    such a code.
    """
    def __init__(self, **kwargs):
        self.colours = [Red, Green, Blue]
        super().__init__(**kwargs)

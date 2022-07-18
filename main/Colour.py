from typing import Tuple

from main.utils.NiceRepr import NiceRepr


class Colour(NiceRepr):
    def __init__(self, name: str, rgb: Tuple[int, int, int]):
        self.name = name
        self.rgb = rgb
        super().__init__(['name'])


Red = Colour('red', (255, 0, 0))
Green = Colour('green', (0, 255, 0))
Blue = Colour('blue', (0, 0, 255))
White = Colour('white', (255, 255, 255))
Black = Colour('black', (0, 0, 0))
Grey = Colour('grey', (128, 128, 128))

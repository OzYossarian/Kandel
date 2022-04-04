from typing import Tuple


class Colour:
    def __init__(self, name: str, rgb: Tuple[int, int, int]):
        self.name = name
        self.rgb = rgb

    def __repr__(self):
        return(self.name)


Red = Colour('red', (255, 0, 0))
Green = Colour('green', (0, 255, 0))
Blue = Colour('blue', (0, 0, 255))
White = Colour('white', (255, 255, 255))
Black = Colour('black', (0, 0, 0))
Grey = Colour('grey', (128, 128, 128))

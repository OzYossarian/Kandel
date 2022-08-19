import random

from main.Colour import Colour


def random_colour():
    rgb = tuple(random.choices(range(255), k=3))
    return Colour(str(rgb), rgb)


def random_colours(n: int):
    rgb_values = random.choices(range(255), k=3 * n)
    # Chunk this sequence into triplets
    rgbs = [
        tuple(rgb_values[3 * i: 3 * (i+1)])
        for i in range(n)]
    # And turn these triplets into colours
    colours = [Colour(str(rgb), rgb) for rgb in rgbs]
    return colours


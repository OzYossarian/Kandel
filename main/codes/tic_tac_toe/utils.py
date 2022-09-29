import random
from typing import List, Tuple

from main.utils.Colour import Red, Green, Blue, Colour
from main.building_blocks.pauli.PauliLetter import PauliY, PauliZ, PauliX, PauliLetter


TicTacToeSquare = Tuple[Colour, PauliLetter]
TicTacToeRoute = List[TicTacToeSquare]

colours = [Red, Green, Blue]
letters = [PauliX, PauliY, PauliZ]
# TODO - recheck my maths around what constitutes a 'good' route - I was
#  omitting initialisation from the stabilizer formalism when I ended up
#  at these colours!
all_good_colours = [
    [Red, Green, Blue],
    [Red, Blue, Green],
    [Green, Blue, Red],
    [Green, Red, Blue],
    [Blue, Red, Green],
    [Blue, Green, Red],
]


def random_valid_route_chunk(length: int):
    route = []
    if length > 0:
        this_square = (random.choice(colours), random.choice(letters))
        route.append(this_square)
        for j in range(1, length):
            # Pick a valid next square.
            next_square = random_valid_next_square(this_square)
            route.append(next_square)
            this_square = next_square
    return route


def random_valid_route(length: int):
    # There are no valid length 0 or 1 routes
    assert length >= 2
    route = random_valid_route_chunk(length - 1)
    # Route is cyclical, so make sure last square is in different column
    # and row to penultimate AND first square of the route.
    last_square = random_valid_sandwiched_square(route[-1], route[0])
    route.append(last_square)
    return route


def random_valid_sandwiched_square(before, after):
    colour = random.choice(
        [c for c in colours if c not in [before[0], after[0]]])
    letter = random.choice(
        [l for l in letters if l not in [before[1], after[1]]])
    return colour, letter


def random_valid_next_square(before):
    colour = random.choice(
        [c for c in colours if c != before[0]])
    letter = random.choice(
        [l for l in letters if l != before[1]])
    return colour, letter


def random_good_route(length):
    assert length == 3 or length >= 5
    good_colours = random.choice(all_good_colours)
    if length == 3:
        valid_letters = [l for c, l in random_valid_route(length)]
        route = list(zip(good_colours, valid_letters))
    else:
        valid_letters = [l for c, l in random_valid_route_chunk(4)]
        route = [(good_colours[i % 3], valid_letters[i]) for i in range(4)]
        for _ in range(length - 5):
            next = random_valid_next_square(route[-1])
            route.append(next)
        sandwich = random_valid_sandwiched_square(route[-1], route[0])
        route.append(sandwich)
    return route


def rest_of_row(colour: Colour, letter: PauliLetter):
    return [
        (c, letter)
        for c in colours
        if c != colour]


def rest_of_column(colour: Colour, letter: PauliLetter):
    return [
        (colour, l)
        for l in letters
        if l != letter]


import random

from main.Colour import Red, Green, Blue
from main.building_blocks.PauliLetter import PauliZ, PauliY, PauliX
from main.codes.hexagonal.tic_tac_toe.TicTacToeCode import TicTacToeCode

colours = [Red, Green, Blue]
letters = [PauliX, PauliY, PauliZ]


def test_follows_tic_tac_toe_rules():
    # Empty list should fail.
    assert not TicTacToeCode.follows_tic_tac_toe_rules([])

    # Test that valid routes are indeed valid.
    repeat = 100
    for i in range(repeat):
        route_length = random.randint(1, 100)
        route = []
        this_colour = random.choice(colours)
        this_letter = random.choice(letters)
        route.append((this_colour, this_letter))

        for j in range(1, route_length-1):
            # Pick a valid next square.
            next_colour = random.choice(
                [c for c in colours if c != this_colour])
            next_letter = random.choice(
                [l for l in colours if l != this_letter])
            route.append((next_colour, next_letter))
            this_colour, this_letter = next_colour, next_letter

        # Route is cyclical, so make sure last square is in different column
        # and row to penultimate AND first square of the route.
        last_colour = random.choice(
            [c for c in colours if c not in [this_colour, route[0][0]]])
        last_letter = random.choice(
            [l for l in colours if l not in [this_letter, route[0][1]]])
        route.append((last_colour, last_letter))

        assert TicTacToeCode.follows_tic_tac_toe_rules(route)

    # Now test bad routes do fail.
    for i in range(repeat):
        fail_at = random.randint(1, 100)
        route = []
        this_colour = random.choice(colours)
        this_letter = random.choice(letters)
        route.append((this_colour, this_letter))

        for j in range(1, fail_at):
            # Pick valid next squares for while...
            next_colour = random.choice(
                [c for c in colours if c != this_colour])
            next_letter = random.choice(
                [l for l in colours if l != this_letter])
            route.append((next_colour, next_letter))
            this_colour, this_letter = next_colour, next_letter

        # ... but now pick a bad square to end with.
        bad_squares = \
            [(c, this_letter) for c in colours] + \
            [(this_colour, l) for l in letters]
        route.append(random.choice(bad_squares))

        assert not TicTacToeCode.follows_tic_tac_toe_rules(route)


def test_is_good_code():
    assert False


def test_create_checks():
    assert False


def test_add_checks_around_plaquette():
    assert False


def test_find_stabilized_plaquettes():
    assert False


def test_reinfer_plaquettes():
    assert False


def test_carry_over_plaquettes():
    assert False


def test_remove_plaquettes():
    assert False


def test_relearn_plaquettes():
    assert False


def test_plan_detectors():
    assert False


def test_time_within_repeating_part_of_code():
    assert False


def test_plan_detectors_of_type():
    assert False


def test_create_detectors():
    assert False

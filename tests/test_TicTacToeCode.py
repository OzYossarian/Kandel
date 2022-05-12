import random

from main.Colour import Red, Green, Blue
from main.building_blocks.PauliLetter import PauliZ, PauliY, PauliX
from main.codes.hexagonal.tic_tac_toe.TicTacToeCode import TicTacToeCode

colours = [Red, Green, Blue]
letters = [PauliX, PauliY, PauliZ]


def random_valid_route_chunk(length: int):
    route = []
    if length > 0:
        this_colour = random.choice(colours)
        this_letter = random.choice(letters)
        route.append((this_colour, this_letter))

        for j in range(1, length):
            # Pick a valid next square.
            next_colour = random.choice(
                [c for c in colours if c != this_colour])
            next_letter = random.choice(
                [l for l in letters if l != this_letter])
            route.append((next_colour, next_letter))
            this_colour, this_letter = next_colour, next_letter

    return route


def test_follows_tic_tac_toe_rules():
    # Empty list should fail.
    assert not TicTacToeCode.follows_tic_tac_toe_rules([])

    # Test that valid routes are indeed valid.
    repeat = 100
    for i in range(repeat):
        route_length = random.randint(1, 100)
        route = random_valid_route_chunk(route_length)
        # Route is cyclical, so make sure last square is in different column
        # and row to penultimate AND first square of the route.
        last_colour = random.choice(
            [c for c in colours if c not in [route[-1][0], route[0][0]]])
        last_letter = random.choice(
            [l for l in colours if l not in [route[-1][1], route[0][1]]])
        route.append((last_colour, last_letter))

        assert TicTacToeCode.follows_tic_tac_toe_rules(route)

    # Now test bad routes do fail.
    for i in range(repeat):
        fail_at = random.randint(1, 100)
        route = random_valid_route_chunk(fail_at)

        # ... but now pick a bad square to end with.
        bad_squares = \
            [(c, route[-1][1]) for c in colours] + \
            [(route[-1][0], l) for l in letters]
        route.append(random.choice(bad_squares))

        assert not TicTacToeCode.follows_tic_tac_toe_rules(route)


def test_is_good_code():
    all_good_colours = [
        [Red, Green, Blue, Red],
        [Red, Blue, Green, Red],
        [Green, Blue, Red, Green],
        [Green, Red, Blue, Green],
        [Blue, Red, Green, Blue],
        [Blue, Green, Red, Blue],
    ]

    # Function allows us to assume route length > 0.
    # So first check all length < 3 routes fail.
    for i in range(100):
        length = random.randint(1, 2)
        route = random_valid_route_chunk(length)
        assert not TicTacToeCode.is_good_code(route)

    # Check 'good' length 3 and 4 routes all work as expected
    for length in [3, 4]:
        for good_colours in all_good_colours:
            valid_letters = [l for c, l in random_valid_route_chunk(length)]
            route = list(zip(good_colours, valid_letters))
            assert TicTacToeCode.is_good_code(route)

    # Now check 'bad' length >= 3 routes are indeed bad.
    for i in range(100):
        length = random.randint(4, 50)
        route = random_valid_route_chunk(length)
        if length == 3:
            route = route + route
        start_colours = [c for c, l in route[:4]]
        if start_colours not in all_good_colours:
            assert not TicTacToeCode.is_good_code(route)


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

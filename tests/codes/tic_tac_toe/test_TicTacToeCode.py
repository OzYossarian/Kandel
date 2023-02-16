import random
from main.codes.tic_tac_toe.HoneycombCode import HoneycombCode

from main.utils.Colour import Red, Green, Blue
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.codes.tic_tac_toe.utils import (
    random_valid_route,
    random_valid_route_chunk,
    all_good_colours,
    random_good_route,
)

colours = [Red, Green, Blue]
letters = [PauliLetter("X"), PauliLetter("Y"), PauliLetter("Z")]
hcc_code = HoneycombCode(4)


def test_follows_tic_tac_toe_rules():
    # There are no valid routes of length < 2
    assert not TicTacToeCode.follows_tic_tac_toe_rules([])
    assert all(
        not TicTacToeCode.follows_tic_tac_toe_rules([(c, l)])
        for c in colours
        for l in letters
    )

    # Test that valid routes are indeed valid.
    repeat = 100
    for i in range(repeat):
        route_length = random.randint(2, 100)
        route = random_valid_route(route_length)
        assert TicTacToeCode.follows_tic_tac_toe_rules(route)

    # Now test bad routes do fail.
    for i in range(repeat):
        fail_at = random.randint(1, 100)
        route = random_valid_route_chunk(fail_at)

        # ... but now pick a bad square to end with.
        bad_squares = [(c, route[-1][1]) for c in colours] + [
            (route[-1][0], l) for l in letters
        ]
        route.append(random.choice(bad_squares))

        assert not TicTacToeCode.follows_tic_tac_toe_rules(route)


def test_is_good_code():
    # Function allows us to assume route length > 1.
    # So first check length 2 routes fail.
    for i in range(100):
        route = random_valid_route_chunk(2)
        assert not TicTacToeCode.is_good_code(route)

    # Check 'good' length 3 routes all work as expected
    for good_colours in all_good_colours:
        valid_letters = [l for c, l in random_valid_route(3)]
        route = list(zip(good_colours, valid_letters))
        assert TicTacToeCode.is_good_code(route)

    # There are no 'good' length 4 routes - check they fail.
    for i in range(100):
        route = random_valid_route(4)
        assert not TicTacToeCode.is_good_code(route)

    # Now check 'bad' 4 != length >= 3 routes are indeed bad.
    for i in range(100):
        length = None
        while length in [None, 4]:
            length = random.randint(3, 50)
        route = random_valid_route(length)
        if length == 3:
            # Since the route is cyclic, we can 'unfold' it once and it
            # still represents exactly the same thing.
            route = route + route
        start_colours = [c for c, l in route[:4]]
        is_good = (
            start_colours[0] == start_colours[3]
            and start_colours[:3] in all_good_colours
        )
        if not is_good:
            assert not TicTacToeCode.is_good_code(route)


def test_create_checks():
    for n in [1, 2, 3, 4, 5]:
        distance = 4 * n
        length = None
        while length in [None, 4]:
            length = random.randint(3, 20)
        route = random_good_route(length)
        # Around every plaquette of colour i there are three edges of colour
        # i+1 which do not border any other plaquette of colour i. So counting
        # the i+1 coloured edges this way gives us exactly all of them. In a
        # 'square' distance 4n code there are 4n^2 plaquettes of each colour.
        # So we should have 3 * 4n^2 checks of each (colour, letter) type.
        code = TicTacToeCode(distance, route)
        for (colour, letter) in set(route):
            checks = code.checks_by_type[(colour, letter)]
            assert len(checks) == 3 * 4 * (n**2)
            # We have the right number of checks - let's check they're in the
            # right places. Count using a different idea to above, so that
            # the test doesn't just use the same code as the method itself.
            plaquette_anchors = code.colourful_plaquette_anchors[colour]
            for anchor in plaquette_anchors:
                every_other_corner = code.get_neighbour_coords(anchor)[::2]
                for u in every_other_corner:
                    diff = (u[0] - anchor[0], u[1] - anchor[1])
                    v = (u[0] + diff[0], u[1] + diff[1])
                    (u, v) = code.wrap_coords(u), code.wrap_coords(v)
                    matches = [
                        check
                        for check in checks
                        if check_is_of_type(check, colour, letter, u, v)
                    ]
                    # Should just be one check matching this spec.
                    assert len(matches) == 1
                    # Remove this check from the list of all checks of this
                    # type, so that we can't satisfy the line above next time
                    # by accidentally finding this check again.
                    checks.remove(matches[0])


def check_is_of_type(check, colour, letter, u, v):
    qubit_coords = {pauli.qubit.coords for pauli in check.paulis.values()}
    pauli_word = {pauli.letter for pauli in check.paulis.values()}
    return qubit_coords == {u, v} and check.colour == colour and pauli_word == {letter}


def test_create_borders():
    for n in [1, 2, 3, 4, 5]:
        distance = 4 * n
        length = None
        # Get a random good route (none of length 4 exist)
        while length in [None, 4]:
            length = random.randint(3, 20)
        route = random_good_route(length)
        code = TicTacToeCode(distance, route)

        # Do the actual assertions within the following method to save
        # us duplicating code.
        def assert_plaquette_borders_correct(anchors, borders_used, e):
            for anchor in anchors:
                corners = code.get_neighbour_coords(anchor)
                for j in range(3):
                    # Loop through corners either anti-clockwise (e = 1) or
                    # clockwise (e = -1)
                    u, v = corners[e * 2 * j], corners[e * (2 * j + 1)]
                    u, v = code.wrap_coords(u), code.wrap_coords(v)
                    for c, l in borders_used:
                        # Find the checks of type (c, l) around this plaquette
                        checks = code.borders[anchor][(c, l)]
                        assert len(checks) == 3
                        # There should be exactly one whose qubits are along
                        # the edge (u, v)
                        matches = [
                            check
                            for check in checks
                            if check_is_of_type(check, c, l, u, v)
                        ]
                        assert len(matches) == 1

        for i in range(3):
            colour = colours[i]
            # Plaquettes of colour i are bordered by checks of colour i+1
            # and i-1 (if these checks are indeed measured)
            borders_plus = set((c, l) for c, l in route if c == colours[(i + 1) % 3])
            borders_minus = set((c, l) for c, l in route if c == colours[(i - 1) % 3])
            anchors = code.colourful_plaquette_anchors[colour]
            if borders_plus:
                assert_plaquette_borders_correct(anchors, borders_plus, 1)
            if borders_minus:
                assert_plaquette_borders_correct(anchors, borders_minus, -1)


def test_find_stabilized_plaquettes():
    stabilized, relearned = hcc_code.find_stabilized_plaquettes()

    # test that after measuring rXX we learn GX and BX
    for stabilized_plaquette, teaching_measurement in stabilized[0].items():
        if stabilized_plaquette == (
            Green,
            PauliLetter("X"),
        ) or stabilized_plaquette == (Blue, PauliLetter("X")):
            assert teaching_measurement == [(0, Red, PauliLetter("X"))]
        else:
            assert teaching_measurement == []

    for stabilized_plaquette, teaching_measurement in stabilized[1].items():
        if stabilized_plaquette == (Blue, PauliLetter("Z")):
            assert teaching_measurement == [
                (0, Red, PauliLetter("X")),
                (1, Green, PauliLetter("Y")),
            ]
        elif stabilized_plaquette == (Blue, PauliLetter("X")):
            assert teaching_measurement == [(0, Red, PauliLetter("X"))]
        elif stabilized_plaquette == (
            Red,
            PauliLetter("Y"),
        ) or stabilized_plaquette == (Blue, PauliLetter("Y")):
            assert teaching_measurement == [(1, Green, PauliLetter("Y"))]
        else:
            assert teaching_measurement == []

    for stabilized_plaquette, bool_relearned in relearned[0].items():
        if stabilized_plaquette in set(
            ((Green, PauliLetter("X")), (Blue, PauliLetter("X")))
        ):
            assert bool_relearned == True
        else:
            assert bool_relearned == False

    for stabilized_plaquette, bool_relearned in relearned[1].items():
        if stabilized_plaquette in set(
            (
                (Red, PauliLetter("Y")),
                (Blue, PauliLetter("Y")),
                (Blue, PauliLetter("Z")),
            )
        ):
            assert bool_relearned == True
        else:
            assert bool_relearned == False


def test_plan_detectors():
    stabilizers, relearned = hcc_code.find_stabilized_plaquettes()
    detector_blueprints = hcc_code.plan_detectors(stabilizers, relearned)
    for drum in detector_blueprints[Red]:
        assert drum.learned == 2

    for drum in detector_blueprints[Blue]:
        assert drum.learned == 1

    for drum in detector_blueprints[Green]:
        assert drum.learned == 0


def test_create_detectors():
    checks, borders = hcc_code.create_checks()
    stabilizers, relearned = hcc_code.find_stabilized_plaquettes()
    detector_blueprints = hcc_code.plan_detectors(stabilizers, relearned)
    detector_schedule = hcc_code.create_detectors(detector_blueprints, borders)

    assert len(detector_schedule) == 3  # honeycomb code has 3 timesteps

    for timestep, detectors_at_timestep in enumerate(detector_schedule):
        assert len(detectors_at_timestep) == 8
        for index in range(1, len(detectors_at_timestep)):

            # in the honeycomb code there are 5 timesteps between floor and lid
            assert detectors_at_timestep[index].start == -4
            assert detectors_at_timestep[index].end == 0


def test_get_init_logical_qubits():
    # Here I use the smallest Honeycomb code because I'm comparing by hand.
    # Ideally I would use a mock class here, but the init function is complicated.

    tic_tac_toe_route = [
        (Red, PauliLetter("X")),
        (Green, PauliLetter("Y")),
        (Blue, PauliLetter("Z")),
    ]
    code = TicTacToeCode(4, tic_tac_toe_route)

    coords_logical_z_horizontal_t0 = set(
        qubit.qubit.coords for qubit in code.logical_qubits[1].z.at_round(-1)
    )
    coords_logical_z_horizontal_t1 = set(
        qubit.qubit.coords for qubit in code.logical_qubits[1].z.at_round(0)
    )
    coords_logical_z_horizontal_t2 = set(
        qubit.qubit.coords for qubit in code.logical_qubits[1].z.at_round(1)
    )

    assert coords_logical_z_horizontal_t0 == {(8, 2), (0, 2), (20, 2), (12, 2)}
    assert coords_logical_z_horizontal_t1 == {(8, 2), (0, 2), (20, 2), (12, 2)}
    assert coords_logical_z_horizontal_t2 == {(2, 4), (6, 4), (14, 4), (18, 4)}

    coords_logical_x_horizontal_t0 = set(
        qubit.qubit.coords for qubit in code.logical_qubits[1].x.at_round(-1)
    )
    coords_logical_x_horizontal_t1 = set(
        qubit.qubit.coords for qubit in code.logical_qubits[1].x.at_round(0)
    )
    coords_logical_x_horizontal_t2 = set(
        qubit.qubit.coords for qubit in code.logical_qubits[1].x.at_round(1)
    )

    assert coords_logical_x_horizontal_t0 == {(6, 0), (8, 2), (8, 6), (6, 8)}  # XX
    assert coords_logical_x_horizontal_t1 == {(6, 4), (8, 2), (8, 10), (6, 8)}  # XX
    assert coords_logical_x_horizontal_t2 == {(6, 4), (8, 2), (8, 10), (6, 8)}  # ZZ

    assert len(coords_logical_x_horizontal_t0 & coords_logical_z_horizontal_t0) == 1
    assert len(coords_logical_x_horizontal_t1 & coords_logical_z_horizontal_t1) == 1
    assert len(coords_logical_x_horizontal_t2 & coords_logical_z_horizontal_t2) == 1

    coords_logical_z_vertical_t0 = set(
        qubit.qubit.coords for qubit in code.logical_qubits[0].z.at_round(-1)
    )
    #    print(code.checks,'checks')
    #    print(code.logical_qubits[0].z.at_round(-1))
    checks_multiplied_in = code.logical_qubits[0].z.update(0)
    assert checks_multiplied_in[0].product.word.word == "XX"
    coords_of_checks_multiplied_in = set(
        pauli.qubit.coords for pauli in checks_multiplied_in[0].paulis.values()
    )
    coords_of_checks_multiplied_in.update(
        set(pauli.qubit.coords for pauli in checks_multiplied_in[1].paulis.values())
    )
    assert coords_of_checks_multiplied_in == {(8, 10), (6, 4), (8, 6), (6, 0)}

    checks_multiplied_in = code.logical_qubits[0].z.update(1)
    assert checks_multiplied_in[0].product.word.word == "YY"
    coords_of_checks_multiplied_in = set(
        pauli.qubit.coords for pauli in checks_multiplied_in[0].paulis.values()
    )
    coords_of_checks_multiplied_in.update(
        set(pauli.qubit.coords for pauli in checks_multiplied_in[1].paulis.values())
    )
    assert coords_of_checks_multiplied_in == {(8, 2), (6, 8), (8, 10), (6, 4)}

    checks_multiplied_in = code.logical_qubits[0].z.update(2)
    assert checks_multiplied_in[0].product.word.word == "ZZ"
    coords_of_checks_multiplied_in = set(
        pauli.qubit.coords for pauli in checks_multiplied_in[0].paulis.values()
    )
    coords_of_checks_multiplied_in.update(
        set(pauli.qubit.coords for pauli in checks_multiplied_in[1].paulis.values())
    )
    assert coords_of_checks_multiplied_in == {(8, 2), (6, 8), (8, 6), (6, 0)}

    checks_multiplied_in = code.logical_qubits[0].z.update(3)
    assert checks_multiplied_in[0].product.word.word == "XX"
    coords_of_checks_multiplied_in = set(
        pauli.qubit.coords for pauli in checks_multiplied_in[0].paulis.values()
    )
    coords_of_checks_multiplied_in.update(
        set(pauli.qubit.coords for pauli in checks_multiplied_in[1].paulis.values())
    )
    assert coords_of_checks_multiplied_in == {(8, 10), (6, 4), (8, 6), (6, 0)}


# def test_reinfer_plaquettes():
#     assert False
#
#
# def test_carry_over_plaquettes():
#     assert False
#
#
# def test_remove_plaquettes():
#     assert False
#
#
# def test_relearn_plaquettes():
#     assert False
#
#
# def test_time_within_repeating_part_of_code():
#     assert False
#
#
# def test_plan_detectors():
#     assert False
#
#
# def test_plan_detectors_of_type():
#     assert False
#
#
# def test_create_detectors():
#     assert False

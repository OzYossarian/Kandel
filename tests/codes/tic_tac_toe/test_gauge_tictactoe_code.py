

from typing import List
from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.gauge_honeycomb_code import GaugeHoneycombCode
from main.utils.Colour import Red, Green, Blue


colours = [Red, Green, Blue]
letters = [PauliLetter("X"), PauliLetter("Y"), PauliLetter("Z")]
hcc_code = GaugeHoneycombCode(4)

def test_plan_detectors_of_type():
    # just do Red X and Red Z?
    stabilized, relearned = hcc_code.find_stabilized_plaquettes()    
    X_red_detector_blueprints = hcc_code.plan_detectors_of_type(Red, PauliLetter('X'), stabilized, relearned)
    assert len(X_red_detector_blueprints) == 2
    assert X_red_detector_blueprints[0].floor == [(-8, Green, PauliLetter('Y')),(-6, Blue, PauliLetter('Z'))]
    assert X_red_detector_blueprints[1].floor == [(-7, Green, PauliLetter('Y')),(-5, Blue, PauliLetter('Z'))]

    assert X_red_detector_blueprints[0].lid == [(-2, Green, PauliLetter('Y')),(0, Blue, PauliLetter('Z'))]
    assert X_red_detector_blueprints[1].lid ==[(-2, Green, PauliLetter('Y')),(0, Blue, PauliLetter('Z'))]

    assert X_red_detector_blueprints[0].learned == 10
    assert X_red_detector_blueprints[1].learned == 4

    Z_red_detector_blueprints = hcc_code.plan_detectors_of_type(Red, PauliLetter('Z'), stabilized, relearned)

    assert len(Z_red_detector_blueprints) == 2

    assert Z_red_detector_blueprints[1].floor == [(-8, Green, PauliLetter('Y')),(-6, Blue, PauliLetter('Z')), (-2, Green, PauliLetter('Y'))]
    assert Z_red_detector_blueprints[0].floor == [(-7, Green, PauliLetter('Y')),(-5, Blue, PauliLetter('Z')), (-2, Green, PauliLetter('Y'))]

    assert Z_red_detector_blueprints[1].lid == [(0, Blue, PauliLetter('Z'))]
    assert Z_red_detector_blueprints[0].lid == [(0, Blue, PauliLetter('Z'))]

    assert Z_red_detector_blueprints[1].learned == 10
    assert Z_red_detector_blueprints[0].learned == 4

    stabilized, relearned = hcc_code.find_stabilized_plaquettes()    
    Z_blue_detector_blueprints = hcc_code.plan_detectors_of_type(Blue, PauliLetter('Z'), stabilized, relearned)

    assert len(Z_blue_detector_blueprints) == 2
    assert Z_blue_detector_blueprints[1].floor == [(-8, Red, PauliLetter('X')),(-6, Green, PauliLetter('Y'))]
    assert Z_blue_detector_blueprints[0].floor == [(-7, Red, PauliLetter('X')),(-5, Green, PauliLetter('Y'))]



def test_find_stabilized_plaquettes():
    stabilized, relearned = hcc_code.find_stabilized_plaquettes()

    # test that after measuring rXX we learn GX and BX
    for stabilized_plaquette, teaching_measurement in stabilized[0].items():
        if stabilized_plaquette == (Green, PauliLetter('X')) or stabilized_plaquette == (Blue, PauliLetter('X')):
            assert teaching_measurement == [(0, Red, PauliLetter('X'))]
        else:
            assert teaching_measurement == []

    for stabilized_plaquette, teaching_measurement in stabilized[1].items():
        if stabilized_plaquette == (Green, PauliLetter('X')) or stabilized_plaquette == (Blue, PauliLetter('X')):
            assert teaching_measurement == [(0, Red, PauliLetter('X'))]
        else:
            assert teaching_measurement == []
    
    for stabilized_plaquette, teaching_measurement in stabilized[2].items():
        if stabilized_plaquette == (Blue, PauliLetter('Z')):
            assert teaching_measurement == [(0, Red, PauliLetter('X')),(2,Green, PauliLetter('Y'))]
        elif stabilized_plaquette == (Blue, PauliLetter('X')):
            assert teaching_measurement == [(0, Red, PauliLetter('X'))]
        elif stabilized_plaquette == (Red, PauliLetter('Y')) or stabilized_plaquette == (Blue, PauliLetter('Y')):
            assert teaching_measurement == [(2, Green, PauliLetter('Y'))]
        else:
            assert teaching_measurement == []

    for stabilized_plaquette, teaching_measurement in stabilized[3].items():
        if stabilized_plaquette == (Blue, PauliLetter('Z')):
            assert teaching_measurement == [(0, Red, PauliLetter('X')),(2,Green, PauliLetter('Y'))]
        elif stabilized_plaquette == (Blue, PauliLetter('X')):
            assert teaching_measurement == [(0, Red, PauliLetter('X'))]
        elif stabilized_plaquette == (Red, PauliLetter('Y')) or stabilized_plaquette == (Blue, PauliLetter('Y')):
            assert teaching_measurement == [(2, Green, PauliLetter('Y'))]
        else:
            assert teaching_measurement == []


    for stabilized_plaquette, bool_relearned in relearned[0].items():
        if stabilized_plaquette in set(((Green, PauliLetter('X')), (Blue, PauliLetter('X')))):
            assert bool_relearned == True
        else: 
            assert bool_relearned == False

    for stabilized_plaquette, bool_relearned in relearned[1].items():
        assert bool_relearned == False

    for stabilized_plaquette, bool_relearned in relearned[2].items():
        if stabilized_plaquette in set(((Red, PauliLetter('Y')), (Blue, PauliLetter('Y')), (Blue, PauliLetter('Z')))):
            assert bool_relearned == True
        else: 
            assert bool_relearned == False

    for stabilized_plaquette, bool_relearned in relearned[3].items():
        assert bool_relearned == False

def test_plan_detectors():
    stabilizers, relearned = hcc_code.find_stabilized_plaquettes()
    detector_blueprints = hcc_code.plan_detectors(stabilizers, relearned)

    for drum in detector_blueprints[Red]:
        assert drum.learned == 4 or drum.learned == 10

    assert len(detector_blueprints[Red]) == 4
    assert detector_blueprints[Red][0].floor == [(-8, Green, PauliLetter('Y')),(-6, Blue, PauliLetter('Z'))]
    assert detector_blueprints[Red][0].lid == [(-2, Green, PauliLetter('Y')),(0, Blue, PauliLetter('Z'))]
    assert detector_blueprints[Red][0].learned == 10

    assert detector_blueprints[Red][1].floor == [(-7, Green, PauliLetter('Y')),(-5, Blue, PauliLetter('Z'))]
    assert detector_blueprints[Red][1].lid == [(-2, Green, PauliLetter('Y')),(0, Blue, PauliLetter('Z'))]
    assert detector_blueprints[Red][1].learned == 4

    assert detector_blueprints[Red][2].floor == [(-7, Green, PauliLetter('Y')),(-5, Blue, PauliLetter('Z')),(-2, Green, PauliLetter('Y'))]
    assert detector_blueprints[Red][2].lid == [(0, Blue, PauliLetter('Z'))]

    assert detector_blueprints[Red][3].floor == [(-8, Green, PauliLetter('Y')),(-6, Blue, PauliLetter('Z')),(-2, Green, PauliLetter('Y'))]
    assert detector_blueprints[Red][3].lid == [(0, Blue, PauliLetter('Z'))]

    for drum in detector_blueprints[Blue]:
        assert drum.learned == 2 or drum.learned == 8

    assert len(detector_blueprints[Blue]) == 4
    assert detector_blueprints[Blue][1].floor == [(-7, Red, PauliLetter('X')),(-5, Green, PauliLetter('Y')), (-2, Red, PauliLetter('X'))]
    assert detector_blueprints[Blue][1].lid == [(0, Green, PauliLetter('Y'))]
    assert detector_blueprints[Blue][1].learned == 8

    for drum in detector_blueprints[Green]:
        assert drum.learned == 0 or drum.learned == 6

    assert len(detector_blueprints[Green]) == 4
    assert detector_blueprints[Green][1].floor == [(-7, Blue, PauliLetter('Z')),(-5, Red, PauliLetter('X')), (-2, Blue, PauliLetter('Z'))]
    assert detector_blueprints[Green][1].lid == [(0, Red, PauliLetter('X'))]
    assert detector_blueprints[Green][1].learned == 0



def test_create_detectors():
    checks, borders = hcc_code.create_checks()
    stabilizers, relearned = hcc_code.find_stabilized_plaquettes()
    detector_blueprints = hcc_code.plan_detectors(stabilizers, relearned)
    detector_schedule = hcc_code.create_detectors(detector_blueprints, borders)


    for detector in detector_schedule[0]:
        for check in detector.lid:
            assert check[0] == 0 or check[0] == -2
        for check in detector.floor:
            assert check[0] == -5 or check[0] == -7 or check[0] == -2
        for check in detector.timed_checks:
            assert check[0] in set((-7,-5,-2,0))

    for detector in detector_schedule[2]:
        for check in detector.lid:
            assert check[0] == 0 or check[0] == -2
        for check in detector.floor:
            assert check[0] == -6 or check[0] == -8 or check[0] == -2
        for check in detector.timed_checks:
            assert check[0] in set((-8,-6,-2,0))


    for detector in detector_schedule[4]:
        for check in detector.lid:
            assert check[0] == 0 or check[0] == -2
        for check in detector.floor:
            assert check[0] == -5 or check[0] == -7 or check[0] == -2
        for check in detector.timed_checks:
            assert check[0] in set((-7,-5,-2,0))


    for detector in detector_schedule[6]:
        for check in detector.lid:
            assert check[0] == 0 or check[0] == -2
        for check in detector.floor:
            assert check[0] == -6 or check[0] == -8 or check[0] == -2
        for check in detector.timed_checks:
            assert check[0] in set((-8,-6,-2,0))

    
    for detector in detector_schedule[8]:
        for check in detector.lid:
            assert check[0] == 0 or check[0] == -2
        for check in detector.floor:
            assert check[0] == -5 or check[0] == -7 or check[0] == -2
        for check in detector.timed_checks:
            assert check[0] in set((-7,-5,-2,0))

    for detector in detector_schedule[10]:
        for check in detector.lid:
            assert check[0] == 0 or check[0] == -2
        for check in detector.floor:
            assert check[0] == -6 or check[0] == -8 or check[0] == -2
        for check in detector.timed_checks:
            assert check[0] in set((-8,-6,-2,0))


test_create_detectors()

def test_create_gauge_detectors():
    checks, borders = hcc_code.create_checks()
    check_schedule = [
            checks[(colour, pauli_letter)]
            for colour, pauli_letter in hcc_code.tic_tac_toe_route] 
    detectors: List[List[Drum]] = [[] for _ in hcc_code.tic_tac_toe_route]

    detectors = hcc_code.create_gauge_detectors(detectors, check_schedule)
    detectors[0] = None
    assert len(detectors[1]) ==12
    assert len(detectors[2]) == 0
    assert len(detectors[3]) == 12
    assert len(detectors[6]) == 0

    
test_create_gauge_detectors()
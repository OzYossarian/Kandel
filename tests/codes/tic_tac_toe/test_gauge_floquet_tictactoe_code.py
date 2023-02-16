from typing import List
from main.building_blocks.detectors.Drum import Drum
from main.building_blocks.pauli.PauliLetter import PauliLetter
#from main.codes.tic_tac_toe.gauge_honeycomb_code import GaugeHoneycombCode
from main.codes.tic_tac_toe.gauge_floquet_colour_code import GaugeFloquetColourCode
#from main.codes.tic_tac_toe.gauge_floquet_tic_tac_toe_code import GaugeColourTicTacToeCode

from main.utils.Colour import Red, Green, Blue


g1_fcc_code = GaugeFloquetColourCode(4, 2)

def test_plan_detectors_of_type():

    #### Test for the Gauge Floquet Colour Code
    stabilized, relearned = g1_fcc_code.find_stabilized_plaquettes()
    X_red_detector_blueprints = g1_fcc_code.plan_detectors_of_type(
        Red, PauliLetter("X"), stabilized, relearned
    )
    Z_red_detector_blueprints = g1_fcc_code.plan_detectors_of_type(
        Red, PauliLetter("Z"), stabilized, relearned)


    print(X_red_detector_blueprints,'here aha')
    print(Z_red_detector_blueprints)


    """
    assert len(X_red_detector_blueprints) == 2
    assert X_red_detector_blueprints[0].floor == [(-8, Green, PauliLetter('Y')),(-6, Blue, PauliLetter('Z'))]
    assert X_red_detector_blueprints[1].floor == [(-7, Green, PauliLetter('Y')),(-5, Blue, PauliLetter('Z'))]

    assert X_red_detector_blueprints[0].lid == [(-2, Green, PauliLetter('Y')),(0, Blue, PauliLetter('Z'))]
    assert X_red_detector_blueprints[1].lid ==[(-2, Green, PauliLetter('Y')),(0, Blue, PauliLetter('Z'))]

    assert X_red_detector_blueprints[0].learned == 10
    assert X_red_detector_blueprints[1].learned == 4
    """


#test_plan_detectors_of_type()
 
def test_create_detectors():
    checks, borders = g1_fcc_code.create_checks()
    stabilizers, relearned = g1_fcc_code.find_stabilized_plaquettes()
    detector_blueprints = g1_fcc_code.plan_detectors(stabilizers, relearned)
    detector_schedule = g1_fcc_code.create_detectors(detector_blueprints, borders)    
    for timestep in detector_schedule:
        for detector in timestep:
#            pass
            print(detector)



    
#def test_detector_scje

test_create_detectors()
def test_create_gauge_detectors():
    checks, borders = g1_fcc_code.create_checks()
    check_schedule = [
        checks[(colour, pauli_letter)]
        for colour, pauli_letter in g1_fcc_code.tic_tac_toe_route
    ]
    detectors: List[List[Drum]] = [[] for _ in g1_fcc_code.tic_tac_toe_route]

    detectors = g1_fcc_code.create_gauge_detectors(detectors, check_schedule)
    detectors[0] = None
    assert len(detectors[1]) == 12
    assert len(detectors[2]) == 0
    assert len(detectors[3]) == 12
    assert len(detectors[6]) == 0


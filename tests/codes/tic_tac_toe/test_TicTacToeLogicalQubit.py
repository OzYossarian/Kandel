from main.codes.tic_tac_toe.FloquetColourCode import FloquetColourCode
from main.codes.tic_tac_toe.HoneycombCode import HoneycombCode
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.codes.tic_tac_toe.gauge_honeycomb_code import GaugeHoneycombCode
from main.codes.tic_tac_toe.logical.TicTacToeLogicalQubit import TicTacToeLogicalQubit

from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
from main.utils.Colour import Blue, Green, Red
from main.building_blocks.pauli.PauliLetter import PauliLetter


class HoneycombCode_permuted(TicTacToeCode):
    """Adaptation of the Honeycomb code where the measurement order has been permuted
    """
    def __init__(self, distance: int):
        tic_tac_toe = [
                (Blue, PauliLetter('Z')),
                (Red, PauliLetter('X')),
                (Green, PauliLetter('Y'))]

        super().__init__(distance, tic_tac_toe)

hcc_code = HoneycombCode(4) 
logical_qubit_hcc_X_vert = TicTacToeLogicalQubit(vertical_pauli_letter=PauliLetter('X'),horizontal_pauli_letter=PauliLetter('Z'), code=hcc_code)
logical_qubit_hcc_Z_vert = TicTacToeLogicalQubit(vertical_pauli_letter=PauliLetter('Z'),horizontal_pauli_letter=PauliLetter('X'), code=hcc_code)

gauge_hcc_code = GaugeHoneycombCode(4)
logical_qubit_gauge_hcc_Z_vert = TicTacToeLogicalQubit(vertical_pauli_letter=PauliLetter('Z'),horizontal_pauli_letter=PauliLetter('X'), code=gauge_hcc_code)

permuted_code = HoneycombCode_permuted(4)
logical_qubit_hcc_p_X_vert = TicTacToeLogicalQubit(vertical_pauli_letter=PauliLetter('X'),horizontal_pauli_letter=PauliLetter('Z'), code=permuted_code)
logical_qubit_hcc_p_Z_vert = TicTacToeLogicalQubit(vertical_pauli_letter=PauliLetter('Z'),horizontal_pauli_letter=PauliLetter('X'), code=permuted_code)

fcc_code = FloquetColourCode(4)
logical_qubit_fcc_X_vert = TicTacToeLogicalQubit(vertical_pauli_letter=PauliLetter('X'),horizontal_pauli_letter=PauliLetter('Z'), code=fcc_code)
logical_qubit_fcc_Z_vert = TicTacToeLogicalQubit(vertical_pauli_letter=PauliLetter('Z'),horizontal_pauli_letter=PauliLetter('X'), code=fcc_code)


def test_get_initial_X_and_Z_boson():
    X_equivalent_bosons, Z_equivalent_bosons, x_initial_boson, z_initial_boson = logical_qubit_hcc_X_vert.get_initial_X_and_Z_boson()
    assert X_equivalent_bosons == [(Green, PauliLetter('X')),(Blue, PauliLetter('X'))]
    assert Z_equivalent_bosons == [(Red, PauliLetter('Y')),(Red, PauliLetter('Z'))]
    assert x_initial_boson == (Green, PauliLetter('X'))
    assert z_initial_boson == (Red, PauliLetter('Y'))

    X_equivalent_bosons, Z_equivalent_bosons, x_initial_boson, z_initial_boson = logical_qubit_hcc_Z_vert.get_initial_X_and_Z_boson()
    assert X_equivalent_bosons == [(Green, PauliLetter('X')),(Blue, PauliLetter('X'))]
    assert Z_equivalent_bosons == [(Red, PauliLetter('Y')),(Red, PauliLetter('Z'))]
    assert x_initial_boson == (Green, PauliLetter('X'))
    assert z_initial_boson == (Red, PauliLetter('Y'))

    X_equivalent_bosons, Z_equivalent_bosons, x_initial_boson, z_initial_boson = logical_qubit_hcc_p_X_vert.get_initial_X_and_Z_boson()
    assert X_equivalent_bosons == [(Blue, PauliLetter('X')),(Blue, PauliLetter('Y'))]
    assert Z_equivalent_bosons == [(Red, PauliLetter('Z')),(Green, PauliLetter('Z'))]
    assert x_initial_boson == (Blue, PauliLetter('X'))
    assert z_initial_boson == (Red, PauliLetter('Z'))

test_get_initial_X_and_Z_boson()

def test_get_next_bosons():
    X_pauli_letters_at_rounds = []
    Z_pauli_letters_at_rounds = []
    for i in range(0,5):
        next_bosons = logical_qubit_hcc_X_vert.get_next_bosons(i)

        X_pauli_letters_at_rounds.append(next_bosons[0][1].letter)
        Z_pauli_letters_at_rounds.append(next_bosons[1][1].letter)
    assert Z_pauli_letters_at_rounds == ['Y', 'Y','X','X','Z']
    assert X_pauli_letters_at_rounds == ['X','Z','Z','Y','Y']

    X_pauli_letters_at_rounds = []
    for i in range(0,11):
        X_pauli_letters_at_rounds.append(logical_qubit_gauge_hcc_Z_vert.get_next_bosons(i)[0][1].letter)
    assert X_pauli_letters_at_rounds == ['X','X','X','Z','Z','Z','Z','Y','Y','Y','Y']

    pauli_letters_at_rounds = []
    for i in range(0,5):
        pauli_letters_at_rounds.append(logical_qubit_hcc_p_X_vert.get_next_bosons(i)[0][1].letter)
    assert pauli_letters_at_rounds == ['X','X','Z','Z','Y']
    
    pauli_letters_at_rounds = []
    for i in range(0,5):
        pauli_letters_at_rounds.append(logical_qubit_hcc_p_Z_vert.get_next_bosons(i)[0][1].letter)
    assert pauli_letters_at_rounds == ['X','X','Z','Z','Y']
    
    pauli_letters_at_rounds = []
    for i in range(-1,5):
        pauli_letters_at_rounds.append(logical_qubit_fcc_X_vert.get_next_bosons(i)[0][1].letter)
    assert pauli_letters_at_rounds == ['X','X','X','X','X','X']
    
    pauli_letters_at_rounds = []
    for i in range(-1,5):
        pauli_letters_at_rounds.append(logical_qubit_fcc_Z_vert.get_next_bosons(i)[0][1].letter)
    assert pauli_letters_at_rounds == ['X','X','X','X','X','X']

    pauli_letters_at_rounds = []
    for i in range(-1,5):
        pauli_letters_at_rounds.append(logical_qubit_hcc_X_vert.get_next_bosons(i)[1][1].letter)
    assert pauli_letters_at_rounds == ['Z','Y','Y','X','X','Z']



def test_get_initial_horizontal_operator():
    x_log_op = logical_qubit_hcc_Z_vert.get_initial_horizontal_operator(PauliLetter('X'),(Blue, PauliLetter('X')))
    x_log_op_coords = set(pauli.qubit.coords for pauli in x_log_op.at_round(-1))
    x_log_op_pauli_letter= set(pauli.letter.letter for pauli in x_log_op.at_round(-1))
    assert x_log_op_coords == {(2, 4), (6, 4), (14, 4), (18, 4)}
    assert x_log_op_pauli_letter == {'X'}

    z_log_op = logical_qubit_hcc_X_vert.get_initial_horizontal_operator(PauliLetter('Z'),(Red, PauliLetter('Z')))
    z_log_op_coords = set(pauli.qubit.coords for pauli in z_log_op.at_round(-1))
    z_log_op_pauli_letter= set(pauli.letter.letter for pauli in z_log_op.at_round(-1))
    assert z_log_op_coords == {(0,2),(8,2),(12,2),(20,2)}
    assert z_log_op_pauli_letter == {'Z'}

    x_log_op = logical_qubit_hcc_p_Z_vert.get_initial_horizontal_operator(PauliLetter('X'),(Blue, PauliLetter('X')))
    x_log_op_coords = set(pauli.qubit.coords for pauli in x_log_op.at_round(-1))
    x_log_op_pauli_letter= set(pauli.letter.letter for pauli in x_log_op.at_round(-1))
    assert x_log_op_coords == {(2, 4), (6, 4), (14, 4), (18, 4)}
    assert x_log_op_pauli_letter == {'X'}

    x_log_op = logical_qubit_hcc_p_X_vert.get_initial_horizontal_operator(PauliLetter('Z'),(Green, PauliLetter('Z')))
    x_log_op_coords = set(pauli.qubit.coords for pauli in x_log_op.at_round(-1))
    x_log_op_pauli_letter= set(pauli.letter.letter for pauli in x_log_op.at_round(-1))
    assert x_log_op_coords == {(20, 6), (12, 6), (8, 6), (0, 6)}
    assert x_log_op_pauli_letter == {'Z'}

    x_log_op = logical_qubit_gauge_hcc_Z_vert.get_initial_horizontal_operator(PauliLetter('X'),(Green, PauliLetter('X')))
    coords_of_logical = set((pauli.qubit.coords for pauli in x_log_op.at_round(-1)))
    assert coords_of_logical == {(0,6),(8,6),(12,6),(20,6)}





def test_get_initial_vertical_operator():
    x_log_op = logical_qubit_hcc_Z_vert.get_initial_horizontal_operator(PauliLetter('Z'),(Red, PauliLetter('Z')))
    x_log_op_coords = set(pauli.qubit.coords for pauli in x_log_op.at_round(-1))
    x_log_op_pauli_letter= set(pauli.letter.letter for pauli in x_log_op.at_round(-1))
    assert x_log_op_coords == {(2, 4), (6, 4), (14, 4), (18, 4)}
    assert x_log_op_pauli_letter == {'Z'}


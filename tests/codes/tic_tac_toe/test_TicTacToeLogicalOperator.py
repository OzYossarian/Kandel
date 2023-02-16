from main.codes.tic_tac_toe.HoneycombCode import HoneycombCode
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.codes.tic_tac_toe.gauge_honeycomb_code import GaugeHoneycombCode
from main.codes.tic_tac_toe.logical.TicTacToeLogicalQubit import TicTacToeLogicalQubit
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models.CodeCapacityBitFlipNoise import CodeCapacityBitFlipNoise
from main.compiling.noise.models.NoNoise import NoNoise
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
from main.utils.Colour import Blue, Green, Red
from main.utils.enums import State
from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
import stim

hcc_code = HoneycombCode(4) 
logical_qubit_hcc_Z_vert = TicTacToeLogicalQubit(vertical_pauli_letter=PauliLetter('Z'),horizontal_pauli_letter=PauliLetter('X'), code=hcc_code)
logical_op_hcc_X_hor = logical_qubit_hcc_Z_vert.x

def test_update():
    checks_t0 = logical_op_hcc_X_hor.update(0)

    coords_of_checks = set((pauli.qubit.coords for check in checks_t0 for pauli in check.paulis.values()))

    assert coords_of_checks == set()
    
    checks_t1 = logical_op_hcc_X_hor.update(1)
    coords_of_checks = set((pauli.qubit.coords for check in checks_t1 for pauli in check.paulis.values()))
    pauli_letter_of_checks = set((pauli.letter for check in checks_t1 for pauli in check.paulis.values())).pop()
    assert coords_of_checks == {(0,6),(8,6),(12,6),(20,6)}
    assert pauli_letter_of_checks == PauliLetter('Y')

    hcc_code = HoneycombCode(4) 
    logical_qubit_hcc_Z_vert = TicTacToeLogicalQubit(vertical_pauli_letter=PauliLetter('Z'),horizontal_pauli_letter=PauliLetter('X'), code=hcc_code)
    logical_op_hcc_Z_ver = logical_qubit_hcc_Z_vert.z

    checks_t0 = logical_op_hcc_Z_ver.update(0)
    coords_of_checks = set((pauli.qubit.coords for check in checks_t0 for pauli in check.paulis.values()))
    assert coords_of_checks == set()
    checks_t1 = logical_op_hcc_Z_ver.update(1)
    coords_of_checks = set((pauli.qubit.coords for check in checks_t1 for pauli in check.paulis.values()))
    pauli_letter_of_checks = set((pauli.letter for check in checks_t1 for pauli in check.paulis.values())).pop()
    assert coords_of_checks == {(6,4),(8,2),(6,8),(8,10)}

    gauge_hcc_code = GaugeHoneycombCode(4,2) 
    logical_qubit_gauge_hcc_Z_vert = TicTacToeLogicalQubit(vertical_pauli_letter=PauliLetter('Z'),
                                                            horizontal_pauli_letter=PauliLetter('X'), code=gauge_hcc_code)
    logical_op_gauge_hcc_X_hor = logical_qubit_gauge_hcc_Z_vert.x
    checks_t0 = logical_op_gauge_hcc_X_hor.update(0)
    coords_of_checks = set((pauli.qubit.coords for check in checks_t0 for pauli in check.paulis.values()))

    assert coords_of_checks == set()

    checks_t1 = logical_op_gauge_hcc_X_hor.update(1)
    coords_of_checks = set((pauli.qubit.coords for check in checks_t1 for pauli in check.paulis.values()))
    assert coords_of_checks == set()

    checks_t2 = logical_op_gauge_hcc_X_hor.update(2)
    coords_of_checks = set((pauli.qubit.coords for check in checks_t2 for pauli in check.paulis.values()))

    assert coords_of_checks == {(0,6),(8,6),(12,6),(20,6)}

hcc_code = HoneycombCode(4) 
logical_qubit_hcc_Z_vert = TicTacToeLogicalQubit(vertical_pauli_letter=PauliLetter('Z'),horizontal_pauli_letter=PauliLetter('X'), code=hcc_code)
logical_op_hcc_X_hor = logical_qubit_hcc_Z_vert.x


def test_at_round():
    logical_op_hcc_X_hor.at_round(-1)
    logical_op_hcc_X_hor.at_round(0)
    coords_of_logical = set((pauli.qubit.coords for pauli in logical_op_hcc_X_hor.at_round(1)))
    assert coords_of_logical == {(0,6),(8,6),(12,6),(20,6)}

    gauge_hcc_code = GaugeHoneycombCode(4,2) 
    logical_qubit_gauge_hcc_Z_vert = TicTacToeLogicalQubit(vertical_pauli_letter=PauliLetter('Z'),
                                                            horizontal_pauli_letter=PauliLetter('X'), code=gauge_hcc_code)
    logical_op_gauge_hcc_X_hor = logical_qubit_gauge_hcc_Z_vert.x
    for i in range(3):
        coords_of_logical = set((pauli.qubit.coords for pauli in logical_op_gauge_hcc_X_hor.at_round(i)))
        x_log_op_pauli_letter= set(pauli.letter.letter for pauli in logical_op_gauge_hcc_X_hor.at_round(i)).pop()

        assert coords_of_logical == {(0,6),(8,6),(12,6),(20,6)}
        assert x_log_op_pauli_letter == 'X'

    for i in range(3,5):
        coords_of_logical = set((pauli.qubit.coords for pauli in logical_op_gauge_hcc_X_hor.at_round(i)))
        x_log_op_pauli_letter= set(pauli.letter.letter for pauli in logical_op_gauge_hcc_X_hor.at_round(i)).pop()

        assert coords_of_logical == {(0,6),(8,6),(12,6),(20,6)}
        assert x_log_op_pauli_letter == 'Z'

    for i in range(5,7):
        coords_of_logical = set((pauli.qubit.coords for pauli in logical_op_gauge_hcc_X_hor.at_round(i)))
        x_log_op_pauli_letter= set(pauli.letter.letter for pauli in logical_op_gauge_hcc_X_hor.at_round(i)).pop()

        assert coords_of_logical == {(6, 8), (14, 8), (18, 8), (2, 8)}
        assert x_log_op_pauli_letter == 'Z'

    for i in range(7,9):
        coords_of_logical = set((pauli.qubit.coords for pauli in logical_op_gauge_hcc_X_hor.at_round(i)))


    gauge_hcc_code = GaugeHoneycombCode(4,2) 
    logical_qubit_gauge_hcc_Z_vert = TicTacToeLogicalQubit(vertical_pauli_letter=PauliLetter('Z'),
                                                            horizontal_pauli_letter=PauliLetter('X'), code=gauge_hcc_code)
    logical_op_gauge_hcc_X_hor = logical_qubit_gauge_hcc_Z_vert.x
    logical_op_gauge_hcc_Z_ver = logical_qubit_gauge_hcc_Z_vert.z

    logical_qubit_gauge_hcc_X_vert = TicTacToeLogicalQubit(vertical_pauli_letter=PauliLetter('X'),
                                                            horizontal_pauli_letter=PauliLetter('Z'), code=gauge_hcc_code)
    logical_op_gauge_hcc_Z_hor = logical_qubit_gauge_hcc_Z_vert.z
    logical_op_gauge_hcc_X_ver = logical_qubit_gauge_hcc_Z_vert.x

    for i in range(10):
        coords_of_logical = set((pauli.qubit.coords for pauli in logical_op_gauge_hcc_Z_hor.at_round(i)))
        print(coords_of_logical)
        # uh oh z vertical is not updating correctly :(
        #coords_of_logical = set((pauli.qubit.coords for pauli in logical_op_gauge_hcc_Z_ver.at_round(i)))
        #print(coords_of_logical)

        # maybe if I fix this it helps

test_at_round()


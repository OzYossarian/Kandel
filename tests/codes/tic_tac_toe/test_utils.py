from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.ColourCodeBosons import ColourCodeBoson
from main.utils.Colour import Red, Green, Blue

def test_mul():

    rz = ColourCodeBoson(Red, PauliLetter('X')) * ColourCodeBoson(Red, PauliLetter('Y'))
    assert rz == ColourCodeBoson(Red, PauliLetter('Z'))

    rx = ColourCodeBoson(Red, PauliLetter('X')) * ColourCodeBoson(Red, PauliLetter('X'))
    assert rx == ColourCodeBoson(Red, PauliLetter('X'))

    gy = ColourCodeBoson(Red, PauliLetter('Y')) * ColourCodeBoson(Blue, PauliLetter('Y'))
    assert gy == ColourCodeBoson(Green, PauliLetter('Y'))


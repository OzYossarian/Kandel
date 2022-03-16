from main.codes.FloquetCode import FloquetCode
from main.codes.HexagonalCode import HexagonalCode
from main.enums import Layout


class HoneycombCode(HexagonalCode, FloquetCode):
    def __init__(self, distance: int, layout: Layout):
        assert distance % 2 == 0
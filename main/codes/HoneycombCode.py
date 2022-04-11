from main.codes.HexaquetCode import HexaquetCode


class HoneycombCode(HexaquetCode):
    def __init__(self, distance: int):
        schedule = ['RX', 'GY', 'BZ']
        super().__init__(distance, schedule)
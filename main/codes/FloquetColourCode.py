from main.codes.HexaquetCode import HexaquetCode


class FloquetColourCode(HexaquetCode):
    def __init__(self, distance: int):
        schedule = ['RX', 'GZ', 'BX', 'RZ', 'GX', 'BZ']
        super().__init__(distance, schedule)
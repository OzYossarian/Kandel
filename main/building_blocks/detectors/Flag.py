from main.building_blocks.detectors.Detector import Detector
from main.building_blocks.pauli import Pauli


class Flag(Detector):
    def __init__(self, pauli: Pauli, end: int):
        raise NotImplementedError()

from typing import Dict, List

from main.building_blocks.pauli.PauliLetter import PauliLetter, PauliX
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import ControlledGateOrderer
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.PauliExtractor import PauliExtractor
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.UniformAncillaBasisExtractor import \
    UniformAncillaBasisExtractor
from main.utils.enums import State


class CzExtractor(UniformAncillaBasisExtractor):
    def __init__(
            self, controlled_gate_orderer: ControlledGateOrderer = None,
            initialisation_instructions: Dict[State, List[str]] = None,
            measurement_instructions: Dict[PauliLetter, List[str]] = None,
            parallelize: bool = True):
        ancilla_basis = PauliX
        pauli_x_extractor = PauliExtractor(['H'], 'CZ', False, ['H'])
        pauli_y_extractor = PauliExtractor(['H_YZ'], 'CZ', False, ['H_YZ'])
        pauli_z_extractor = PauliExtractor([], 'CZ', False, [])
        pauli_extractors = {
            PauliLetter('X'): pauli_x_extractor,
            PauliLetter('Y'): pauli_y_extractor,
            PauliLetter('Z'): pauli_z_extractor}
        super().__init__(
            ancilla_basis,
            pauli_extractors,
            controlled_gate_orderer,
            initialisation_instructions,
            measurement_instructions,
            parallelize)

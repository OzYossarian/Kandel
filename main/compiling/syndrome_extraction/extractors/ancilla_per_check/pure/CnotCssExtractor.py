from typing import Dict, List

from main.building_blocks.pauli.PauliLetter import PauliX, PauliZ, PauliLetter
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import ControlledGateOrderer
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.PauliExtractor import PauliExtractor
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.pure.PurePauliWordExtractor import PurePauliWordExtractor
from main.utils.enums import State


class CnotCssExtractor(PurePauliWordExtractor):
    def __init__(
            self, controlled_gate_orderer: ControlledGateOrderer = None,
            initialisation_instructions: Dict[State, List[str]] = None,
            measurement_instructions: Dict[PauliLetter, List[str]] = None,
            parallelize: bool = True):
        x_word_ancilla_basis = PauliX
        z_word_ancilla_basis = PauliZ
        pauli_x_extractor = PauliExtractor([], 'CNOT', True, [])
        pauli_z_extractor = PauliExtractor([], 'CNOT', False, [])
        super().__init__(
            x_word_ancilla_basis=x_word_ancilla_basis,
            z_word_ancilla_basis=z_word_ancilla_basis,
            pauli_x_extractor=pauli_x_extractor,
            pauli_z_extractor=pauli_z_extractor,
            controlled_gate_orderer=controlled_gate_orderer,
            initialisation_instructions=initialisation_instructions,
            measurement_instructions=measurement_instructions,
            parallelize=parallelize)

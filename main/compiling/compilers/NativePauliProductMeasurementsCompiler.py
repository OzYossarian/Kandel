from typing import List, Dict

from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.compilers.Compiler import Compiler
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.syndrome_extraction.extractors.SyndromeExtractor import SyndromeExtractor
from main.enums import State


class NativePauliProductMeasurementsCompiler(Compiler):
    def __init__(
            self, noise_model: NoiseModel = None,
            syndrome_extractor: SyndromeExtractor = None,
            initialisation_instructions: Dict[State, List[str]] = None,
            measurement_instructions: Dict[PauliLetter, List[str]] = None):
        super().__init__(
            noise_model, syndrome_extractor, initialisation_instructions,
            measurement_instructions)

    def add_ancilla_qubits(self, code):
        # No need!
        pass

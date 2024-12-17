from typing import List, Dict

from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.compilers.Compiler import Compiler
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.syndrome_extraction.extractors.NativePauliProductMeasurementsExtractor import \
    NativePauliProductMeasurementsExtractor
from main.utils.enums import State


class NativePauliProductMeasurementsCompiler(Compiler):
    def __init__(
            self, noise_model: NoiseModel = None,
            syndrome_extractor: NativePauliProductMeasurementsExtractor = None,
            initialisation_instructions: Dict[State, List[str]] = None):
        if syndrome_extractor is None:
            syndrome_extractor = NativePauliProductMeasurementsExtractor(parallelize=True)
        # We pass None for measurement_instructions, 
        # but the base class will still set some default measurement 
        # instructions for single qubit measurements.
        super().__init__(
            noise_model, 
            syndrome_extractor, 
            initialisation_instructions, 
            measurement_instructions=None)

    def add_ancilla_qubits(self, code):
        # No need!
        pass

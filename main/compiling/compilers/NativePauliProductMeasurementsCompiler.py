from main.compiling.compilers.Compiler import Compiler
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.syndrome_extraction.extractors.SyndromeExtractor import SyndromeExtractor


class NativePauliProductMeasurementsCompiler(Compiler):
    def __init__(
            self, noise_model: NoiseModel,
            syndrome_extractor: SyndromeExtractor):
        super().__init__(noise_model, syndrome_extractor)

    def add_ancilla_qubits(self, code):
        # No need!
        pass

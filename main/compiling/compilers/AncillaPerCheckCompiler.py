from main.building_blocks.Qubit import Qubit
from main.codes.Code import Code
from main.compiling.compilers.Compiler import Compiler
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.syndrome_extraction.extractors.SyndromeExtractor import SyndromeExtractor


class AncillaPerCheckCompiler(Compiler):
    def __init__(
            self, noise_model: NoiseModel,
            syndrome_extractor: SyndromeExtractor):
        super().__init__(noise_model, syndrome_extractor)

    def add_ancilla_qubits(self, code: Code):
        for check in code.checks:
            # For each check, just create an ancilla wherever the anchor is
            if check.ancilla is None:
                check.ancilla = Qubit(check.anchor)

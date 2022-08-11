from typing import List, Dict

from main.building_blocks.Qubit import Qubit
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.Code import Code
from main.compiling.compilers.Compiler import Compiler
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.syndrome_extraction.extractors.SyndromeExtractor import SyndromeExtractor
from main.enums import State


class AncillaPerCheckCompiler(Compiler):
    def __init__(
            self, noise_model: NoiseModel = None,
            syndrome_extractor: SyndromeExtractor = None,
            initialisation_instructions: Dict[State, List[str]] = None,
            measurement_instructions: Dict[PauliLetter, List[str]] = None):
        super().__init__(
            noise_model,
            syndrome_extractor,
            initialisation_instructions,
            measurement_instructions)

    def add_ancilla_qubits(self, code: Code):
        for check in code.checks:
            if check.ancilla is None:
                # For each check, just create an ancilla wherever the anchor is -
                # or use the one that's already there.
                if check.anchor in code.ancilla_qubits:
                    ancilla = code.ancilla_qubits[check.anchor]
                else:
                    ancilla = Qubit(check.anchor)
                    code.ancilla_qubits[check.anchor] = ancilla
                check.ancilla = ancilla

from typing import Dict, List

from main.building_blocks.Check import Check
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import ControlledGateOrderer
from main.compiling.syndrome_extraction.extractors.PauliExtractor import PauliExtractor
from main.compiling.syndrome_extraction.extractors.mixed.UniformAncillaBasisExtractor import \
    UniformAncillaBasisExtractor
from main.enums import State


class PurePauliWordExtractor(UniformAncillaBasisExtractor):
    def __init__(
            self,
            x_word_ancilla_basis: PauliLetter = None,
            y_word_ancilla_basis: PauliLetter = None,
            z_word_ancilla_basis: PauliLetter = None,
            pauli_x_extractor: PauliExtractor = None,
            pauli_y_extractor: PauliExtractor = None,
            pauli_z_extractor: PauliExtractor = None,
            controlled_gate_orderer: ControlledGateOrderer = None,
            initialisation_instructions: Dict[State, List[str]] = None,
            measurement_instructions: Dict[PauliLetter, List[str]] = None,
            parallelize: bool = True):
        # This extractor is optimised for codes where every check is a
        # 'pure' pauli word - i.e. just one repeated letter, e.g. surface code
        # (always XX...X or ZZ...Z), repetition code (always ZZ) or
        # tic-tac-toe code (always XX, YY or ZZ). It allows ancillas of
        # different check types to be initialised (and measured) in different
        # bases to one another.

        super().__init__(
            pauli_x_extractor=pauli_x_extractor,
            pauli_y_extractor=pauli_y_extractor,
            pauli_z_extractor=pauli_z_extractor,
            controlled_gate_orderer=controlled_gate_orderer,
            initialisation_instructions=initialisation_instructions,
            measurement_instructions=measurement_instructions,
            parallelize=parallelize)

        self.x_word_ancilla_basis = x_word_ancilla_basis
        self.y_word_ancilla_basis = y_word_ancilla_basis
        self.z_word_ancilla_basis = z_word_ancilla_basis

    def get_ancilla_basis(self, check: Check) -> PauliLetter:
        if check.product.word.word == 'X' * check.weight:
            return self.x_word_ancilla_basis \
                if self.x_word_ancilla_basis is not None \
                else self._no_ancilla_basis_error(check, 'XX...X')
        elif check.product.word.word == 'Y' * check.weight:
            return self.y_word_ancilla_basis \
                if self.y_word_ancilla_basis is not None \
                else self._no_ancilla_basis_error(check, 'YY...Y')
        elif check.product.word.word == 'Z' * check.weight:
            return self.z_word_ancilla_basis \
                if self.z_word_ancilla_basis is not None \
                else self._no_ancilla_basis_error(check, 'ZZ...Z')
        else:
            raise ValueError(
                f"Can't use a PurePauliWordExtractor to extract syndrome of "
                f"a check whose product is a mixed Pauli word! The relevant "
                f"check is: {check}.")

    @staticmethod
    def _no_ancilla_basis_error(check: Check, word: str):
        raise ValueError(
            f"Tried to extract syndrome for {word} check but no "
            f"ancilla basis was provided to the PurePauliWordExtractor "
            f"for such a check! The relevant check is: {check}")

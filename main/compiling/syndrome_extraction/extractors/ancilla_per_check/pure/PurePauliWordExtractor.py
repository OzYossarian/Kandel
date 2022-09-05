from typing import Dict, List

from main.building_blocks.Check import Check
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import ControlledGateOrderer
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.PauliExtractor import PauliExtractor
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.UniformAncillaBasisExtractor import \
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
        """
        This extractor is optimised for codes where every check is a 'pure'
        Pauli word - i.e. either XX...X, ZZ...Z or YY...Y. Such codes include
        the surface code (always XX...X or ZZ...Z), repetition code (always
        ZZ) and tic-tac-toe codes (always XX, YY or ZZ). It allows ancillas
        of different check types to be initialised (and measured) in
        different bases to one another.

        Args:
            x_word_ancilla_basis:
                The basis in which to initialise and measure the ancilla
                qubits for XX...X checks
            y_word_ancilla_basis:
                The basis in which to initialise and measure the ancilla
                qubits for YY...Y checks
            z_word_ancilla_basis:
                The basis in which to initialise and measure the ancilla
                qubits for ZZ...Z checks
            pauli_x_extractor:
                Data concerning how to extract a Pauli X within an XX...X check
            pauli_y_extractor:
                Data concerning how to extract a Pauli Y within a YY...Y check
            pauli_z_extractor:
                Data concerning how to extract a Pauli X within a ZZ...Z check
            controlled_gate_orderer:
                Class that will define the order in which data qubits are
                'extracted' (i.e. order in which we place controlled gates
                between data qubits and ancilla qubits).
                    If `None`, we use the trivial ordering, which is the order
                in which the Paulis are listed within the check. This may lead
                to exceptions, either because it means we try to place two
                gates at the same time on the same qubit, or because we don't
                actually implement the desired measurement.
            initialisation_instructions:
                Names of gates that implement initialisation into the Pauli
                eigenstates. e.g. initialising into |+> state might be
                implemented via ['RZ', 'H'] (meaning initialise into |0> then
                do a Hadamard gate).
                    If `None`, defaults to the instructions used by the
                compiler.
            measurement_instructions:
                Names of gates that implement measurement in the Pauli bases.
                e.g. measuring in X basis might be implemented via ['H' 'MZ']
                (meaning do a Hadamard gate then measure in Z basis).
                    If `None`, defaults to the instructions used by the
                compiler.
            parallelize:
                Whether to extract all checks' syndromes for a given round in
                parallel.
        """

        pauli_extractors = {
            PauliLetter('X'): pauli_x_extractor,
            PauliLetter('Y'): pauli_y_extractor,
            PauliLetter('Z'): pauli_z_extractor}

        super().__init__(
            None,
            pauli_extractors,
            controlled_gate_orderer,
            initialisation_instructions,
            measurement_instructions,
            parallelize)

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
                f"a check whose product is not XX...X, YY...Y or ZZ...Z! "
                f"The relevant check is: {check}.")

    @staticmethod
    def _no_ancilla_basis_error(check: Check, word: str):
        raise ValueError(
            f"Tried to extract syndrome for {word} check but no "
            f"ancilla basis was provided to the PurePauliWordExtractor "
            f"for such a check! The relevant check is: {check}")

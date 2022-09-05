from __future__ import annotations

from typing import List, Dict

from main.building_blocks.Check import Check
from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliZ, PauliX, PauliY, PauliLetter
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.AncillaPerCheckExtractor import AncillaPerCheckExtractor
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.PauliExtractor import PauliExtractor
from main.compiling.Instruction import Instruction
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import ControlledGateOrderer
from main.enums import State


class UniformAncillaBasisExtractor(AncillaPerCheckExtractor):
    def __init__(
            self, ancilla_basis: PauliLetter,
            pauli_extractors: Dict[PauliLetter, PauliExtractor | None],
            controlled_gate_orderer: ControlledGateOrderer = None,
            initialisation_instructions: Dict[State, List[str]] = None,
            measurement_instructions: Dict[PauliLetter, List[str]] = None,
            parallelize: bool = True):
        """
        A syndrome extractor that initialises and measures all ancilla qubits
        in the same basis.
        Args:
            ancilla_basis:
                The basis in which to initialise and measure all ancilla qubits
            pauli_extractors:
                Specifies how to extract a Pauli with a given letter within
                a larger Pauli word, e.g. how to extract an X within XYZXYZ.
                Each key is a PauliLetter, and each value is a PauliExtractor;
                the latter is just a container for the data specifying how
                to extract the key. To specify that nothing needs to be done
                for a given PauliLetter, add it as a key whose value is None.
                By default, this is the behaviour of PauliLetter('I'), unless
                something different is passed in.
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
        # TODO - could check here that the given rotations and controlled
        #  gates really do extract the right syndromes?

        super().__init__(
            controlled_gate_orderer,
            initialisation_instructions,
            measurement_instructions,
            parallelize)

        # The reason we don't raise an error here if ancilla basis is None is
        # because PurePauliWordExtractor inherits from this class, and in
        # that class it makes sense to have ancilla_basis set to None,
        # because there we instead have an ancilla basis per check type
        # (XX..X, YY...Y and ZZ...Z). Instead, we raise an error in the
        # get_ancilla_basis method if necessary.
        self.ancilla_basis = ancilla_basis
        self.pauli_extractors = pauli_extractors
        if PauliLetter('I') not in self.pauli_extractors:
            self.pauli_extractors[PauliLetter('I')] = None

    def get_ancilla_basis(self, check: Check) -> PauliLetter:
        if self.ancilla_basis is not None:
            return self.ancilla_basis
        else:
            raise ValueError(
                "Must tell the SyndromeExtractor the basis in "
                "which to initialise and measure all ancillas.")

    def get_pre_rotations(
            self, pauli: Pauli, check: Check) -> List[Instruction]:
        if pauli.letter in self.pauli_extractors:
            extractor = self.pauli_extractors[pauli.letter]
            if extractor is not None:
                return [
                    Instruction([pauli.qubit], name)
                    for name in extractor.pre_rotations]
            else:
                return []
        else:
            self._no_extraction_method_error(pauli, check)

    def get_post_rotations(
            self, pauli: Pauli, check: Check) -> List[Instruction]:
        if pauli.letter in self.pauli_extractors:
            extractor = self.pauli_extractors[pauli.letter]
            if extractor is not None:
                return [
                    Instruction([pauli.qubit], name)
                    for name in extractor.post_rotations]
            else:
                return []
        else:
            self._no_extraction_method_error(pauli, check)

    def get_controlled_gate(
            self, pauli: Pauli, check: Check) -> Instruction | None:
        if pauli.letter in self.pauli_extractors:
            extractor = self.pauli_extractors[pauli.letter]
            if extractor is not None:
                qubits = [check.ancilla, pauli.qubit] \
                    if extractor.ancilla_is_control \
                    else [pauli.qubit, check.ancilla]
                return Instruction(qubits, extractor.controlled_gate)
            else:
                return None
        else:
            self._no_extraction_method_error(pauli, check)

    @staticmethod
    def _no_extraction_method_error(pauli: Pauli, check: Check):
        raise ValueError(
            f"No data was given to the SyndromeExtractor "
            f"specifying how to extract pauli {pauli} as part of check "
            f"{check}.")

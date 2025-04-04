from __future__ import annotations

from typing import Iterable, TYPE_CHECKING

from main.building_blocks.Check import Check
from main.compiling.Circuit import Circuit
if TYPE_CHECKING:
    from main.compiling.compilers.Compiler import Compiler
from main.compiling.Instruction import Instruction
from main.compiling.syndrome_extraction.extractors import SyndromeExtractor
from main.utils.types import Tick


class NativePauliProductMeasurementsExtractor(SyndromeExtractor):
    def __init__(self, parallelize: bool = True):
        """
        A syndrome extractor that can use native Pauli product measurements.

        Args:
            parallelize:
                Whether to extract all checks' syndromes for a given round in
                parallel.
        """
        super().__init__(parallelize)

    def extract_checks(
            self,
            checks: Iterable[Check],
            round: int,
            tick: int,
            circuit: Circuit,
            compiler: Compiler) -> Tick:
        if self.parallelize:
            # Check no qubit is involved in more than one check.
            qubits = [
                pauli.qubit for check in checks for pauli in check.paulis.values()]
            if len(qubits) != len(set(qubits)):
                raise ValueError(
                    f"At least one qubit is involved in more than one check at round {round}: {checks}.")
            return self._extract_checks_in_parallel(checks, round, tick, circuit, compiler)
        else:
            return self._extract_checks_in_sequence(checks, round, tick, circuit, compiler)

    def _extract_checks_in_parallel(
            self,
            checks: Iterable[Check],
            round: int,
            tick: int,
            circuit: Circuit,
            compiler: Compiler) -> Tick:
        for check in checks:
            self._extract_check(check, round, tick, circuit, compiler)
        # Return next available non-noise tick.
        return tick + 2

    def _extract_checks_in_sequence(
            self,
            checks: Iterable[Check],
            round: int,
            tick: int,
            circuit: Circuit,
            compiler: Compiler) -> Tick:
        for check in checks:

            self._extract_check(check, round, tick, circuit, compiler)
            tick += 2
        return tick

    def _extract_check(
            self,
            check: Check,
            round: int,
            tick: int,
            circuit: Circuit,
            compiler: Compiler):

        qubits = [pauli.qubit for pauli in check.paulis.values()]

        if compiler.noise_model.before_mpp_noise is not None:
            noise_instruction = compiler.noise_model.before_mpp_noise.instruction(
                qubits)
            circuit.add_instruction(tick-1, noise_instruction)

        if compiler.noise_model.measurement is not None:
            noise_param = compiler.noise_model.measurement.params
        else:
            noise_param = ()
            
        instruction = Instruction(
            qubits, "MPP", noise_param, is_measurement=True)
        circuit.measure(instruction, check, round, tick)

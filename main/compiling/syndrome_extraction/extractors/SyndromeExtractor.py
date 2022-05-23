from __future__ import annotations

from typing import TYPE_CHECKING

from main.building_blocks.Check import Check
from main.building_blocks.Pauli import Pauli
from main.building_blocks.PauliLetter import PauliZ, PauliX, PauliY
from main.building_blocks.Qubit import Qubit
from main.compiling.Circuit import Circuit
if TYPE_CHECKING:
    from main.compiling.compilers.Compiler import Compiler
from main.compiling.Gate import Gate
from main.compiling.noise.models.NoiseModel import NoiseModel
from main.compiling.syndrome_extraction.cnot_order.CNOTOrderer import CNOTOrderer
from main.enums import State


class SyndromeExtractor:
    def __init__(self, cnot_orderer: CNOTOrderer = None):
        # This extractor will work for any pauli word stabilizer,
        # but won't necessarily give an optimal circuit.
        self.cnot_orderer = cnot_orderer

    def extract_check(
            self, tick: int, check: Check, circuit: Circuit,
            compiler: Compiler, round: int, ancilla_state: State = State.Zero,
            ancilla_measurement_basis: Pauli = PauliZ):

        # First intialise the ancilla qubit.
        check.ancilla.initial_state = ancilla_state
        tick = compiler.initialize_qubits([check.ancilla], tick, circuit)

        # Now place CNOTs between data qubits and the ancilla, possibly with
        # some rotation gates on data qubits too.
        ordered_paulis = self.cnot_orderer.order(check)
        for pauli in ordered_paulis:
            tick = self.extract_pauli(
                pauli, check.ancilla, tick, circuit, compiler.noise_model)

        # Now measure the ancilla to get the check measurement result.
        tick = compiler.measure_qubit(
            check.ancilla, tick, ancilla_measurement_basis,
            circuit, check, round)
        return tick

    def extract_pauli(
            self, pauli: Pauli, ancilla: Qubit, tick: int,
            circuit: Circuit, noise_model: NoiseModel):

        if pauli is not None:
            if pauli.letter == PauliZ:
                # No extra gates needed
                pre_rotate = None
                post_rotate = None
            elif pauli.letter == PauliX:
                # Rotate so that this data qubit is effectively in Z basis
                pre_rotate = Gate([pauli.qubit], 'H')
                post_rotate = Gate([pauli.qubit], 'H')
            else:
                assert pauli.letter == PauliY
                # Again, rotate so that this data qubit is in Z basis
                pre_rotate = Gate([pauli.qubit], 'SQRT_X')
                post_rotate = Gate([pauli.qubit], 'SQRT_X_DAG')

            def rotate(rotation_gate, rotation_tick):
                if rotation_gate is not None:
                    circuit.add_gate(rotation_tick, rotation_gate)
                    noise = noise_model.one_qubit_gate
                    if noise is not None:
                        circuit.add_noise(rotation_tick + 1, noise.gate([pauli.qubit]))

            cnot = Gate([pauli.qubit, ancilla], 'CNOT')
            rotate(pre_rotate, tick)
            circuit.add_gate(tick + 2, cnot)
            noise = noise_model.two_qubit_gate
            if noise is not None:
                circuit.add_noise(tick + 3, noise.gate([pauli.qubit, ancilla]))
            rotate(post_rotate, tick + 4)

        return tick + 6

    @property
    def extract_checks_sequentially(self):
        # TODO - this might be better off as just a bool passed into the
        #  compiler or something?
        return self.cnot_orderer is None

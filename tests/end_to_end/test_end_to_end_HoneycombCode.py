

from typing import List

import stim

from main.building_blocks.detectors import Stabilizer
from main.codes.tic_tac_toe import HoneycombCode
from main.compiling.compilers import NativePauliProductMeasurementsCompiler
from main.compiling.noise.models import EM3
from main.compiling.syndrome_extraction.extractors import NativePauliProductMeasurementsExtractor


def generate_circuit() -> stim.Circuit:
    code = HoneycombCode(4)
    logical_observables = [code.logical_qubits[1].x]
    initial_stabilizers = []
    for check in code.check_schedule[0]:
        initial_stabilizers.append(Stabilizer([(0, check)], 0))

    compiler = NativePauliProductMeasurementsCompiler(
        noise_model=EM3(0.1),
        syndrome_extractor=NativePauliProductMeasurementsExtractor(),

    )
    stim_circuit = compiler.compile_to_stim(
        code=code,
        total_rounds=6,
        initial_stabilizers=initial_stabilizers,
        observables=logical_observables,
    )
    return stim_circuit


def test_number_of_two_qubit_errors():

    circ : stim.Circuit = generate_circuit()
    # circuit conists of 6 measurement rounds
    assert str(circ).count("PAULI_CHANNEL_2") == 6

    # PAULI_CHANNEL_1 only occurs after qubit initialization
    assert str(circ).count("PAULI_CHANNEL_1") == 3
    

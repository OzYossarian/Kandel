from datetime import datetime
from pathlib import Path
from typing import Callable

import sinter
from matplotlib import pyplot as plt

from main.building_blocks.pauli.Pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.FloquetColourCode import FloquetColourCode
from main.codes.tic_tac_toe.HoneycombCode import HoneycombCode
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models import CircuitLevelNoise
from main.compiling.noise.models.PhenomenologicalNoise import PhenomenologicalNoise
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import TrivialOrderer
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.UniformAncillaBasisExtractor import \
    UniformAncillaBasisExtractor
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
from main.utils.enums import State
from main.utils.utils import output_path


def tic_tac_toe_phenom_tasks(constructor: Callable[[int], TicTacToeCode]):
    tasks = []
    syndrome_extractor = CxCyCzExtractor(TrivialOrderer())
    error_rates = [0.001, 0.0015, 0.002, 0.0035, 0.003]
    distances = [4, 8, 12]
    for error_rate in error_rates:
        print(f'Error rate: {error_rate}')
        for distance in distances:
            print(f'Distance: {distance}')
            tasks.append(tic_tac_toe_phenom_task(
                constructor, distance, error_rate, syndrome_extractor))
    return tasks


def tic_tac_toe_phenom_task(
        constructor: Callable[[int], TicTacToeCode],
        distance: int, error_rate: float, syndrome_extractor: UniformAncillaBasisExtractor):
    noise_model = CircuitLevelNoise(error_rate, error_rate, error_rate, error_rate, error_rate)
    compiler = AncillaPerCheckCompiler(noise_model, syndrome_extractor)

    code = constructor(distance)
    data_qubits = list(code.data_qubits.values())
    initial_states = {qubit: State.Plus for qubit in data_qubits}
    final_measurements = [Pauli(qubit, PauliLetter('X')) for qubit in data_qubits]
    observables = [code.logical_qubits[1].x]
    circuit = compiler.compile_code(
        code=code,
        layers=distance,
        initial_states=initial_states,
        final_measurements=final_measurements,
        logical_observables=observables)
    return sinter.Task(
        circuit=circuit,
        json_metadata={
            'distance': distance,
            'error_rate': error_rate})


def main():
    # Collect the samples (takes a few minutes).
    tasks = tic_tac_toe_phenom_tasks(FloquetColourCode)
    samples = sinter.collect(
        tasks=tasks,
        hint_num_tasks=len(tasks),
        num_workers=4,
        max_shots=1000,
        max_errors=100,
        decoders=['pymatching'],
        print_progress=True
    )

    # Save samples as CSV data.
    filename = 'FloquetColourCode'
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{output_path()}/{filename}_{now}'
    Path(Path(filename).parent).mkdir(parents=True, exist_ok=True)

    with open(f'{filename}.csv', 'w') as file:
        file.write(sinter.CSV_HEADER)
        for sample in samples:
            file.write(sample.to_csv_line())

    # Render a matplotlib plot of the data.
    fig, ax = plt.subplots(1, 1)
    sinter.plot_error_rate(
        ax=ax,
        stats=samples,
        group_func=lambda stat: f"FCC, d={stat.json_metadata['distance']}",
        x_func=lambda stat: stat.json_metadata['error_rate'],
    )
    ax.loglog()
    ax.set_ylim(1e-5, 1)
    ax.grid()
    ax.set_title('Logical Error Rate vs Physical Error Rate')
    ax.set_ylabel('Logical Error Probability (per shot)')
    ax.set_xlabel('Circuit-Level Noise Model Parameter')
    ax.legend()

    # Save to file and also open in a window.
    fig.savefig(f'{filename}.png')
    plt.show()


# NOTE: This is actually necessary! If the code inside 'main()' was at the
# module level, the multiprocessing children spawned by sinter.collect would
# also attempt to run that code.
if __name__ == '__main__':
    main()

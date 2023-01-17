import hashlib
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Callable

import stim
from scipy.optimize import curve_fit

import sinter
from matplotlib import pyplot as plt

from main.building_blocks.pauli import Pauli
from main.building_blocks.pauli.PauliLetter import PauliLetter
from main.codes.tic_tac_toe.FloquetColourCode import FloquetColourCode
from main.codes.tic_tac_toe.HoneycombCode import HoneycombCode
from main.codes.tic_tac_toe.TicTacToeCode import TicTacToeCode
from main.compiling.compilers.AncillaPerCheckCompiler import AncillaPerCheckCompiler
from main.compiling.noise.models import CircuitLevelNoise
from main.compiling.syndrome_extraction.extractors.ancilla_per_check.mixed.CxCyCzExtractor import CxCyCzExtractor
from main.utils.enums import State
from main.utils.utils import output_path


"""
Let m be measurement noise parameter and let all other circuit-level noise parameters equal q.
Let M be number of measurement gates and Q be number of all other non-noise gates.
Define:

bias = m/q, 
p = (m.M + q.Q) / M + Q

Want to solve for m and q. 

m = q.bias
-> p = (q.bias.M + q.Q) / M + Q
-> (M + Q)p = q(bias.M + Q)
-> q = (M + Q)p / (bias.M + Q)

Alternatively:
q = m/bias
-> p = (m.M + (m/bias).Q) / M + Q
-> p = m(M + Q/bias) / M + Q
-> (M + Q)p = m(M + Q/bias)
-> m = (M + Q)p / (M + Q/bias)


"""


def get_bias_tasks(constructor: Callable[[int], TicTacToeCode]):
    # biases = [1/8, 1/4, 1/2, 1, 2, 4, 8]
    biases = [64, 128]
    # distances = [4, 8, 12, 16]
    distances = [4, 8, 12, 16]
    ps = [0.0015, 0.002, 0.0025]
    # ps = [0.001, 0.004, 0.005, 0.006]

    syndrome_extractor = CxCyCzExtractor()
    # We'll first compile to our own Circuit class to calculate the number
    # of locations Q where noise could be added. Then we'll use this Q to
    # calculate m and q, and then compile to a stim.Circuit using these
    # parameters.
    pre_compiler = AncillaPerCheckCompiler(
        noise_model=CircuitLevelNoise(1, None, 1, 1, None),
        syndrome_extractor=syndrome_extractor)

    tasks = defaultdict(list)
    for bias in biases:
        print(f"Bias = {bias}")
        for distance in distances:
            print(f"Distance = {distance}")
            code = constructor(distance)
            data_qubits = code.data_qubits.values()
            initial_states = {qubit: State.Plus for qubit in data_qubits}
            final_measurements = [
                Pauli(qubit, PauliLetter('X')) for qubit in data_qubits]
            observables = [code.logical_qubits[1].x]
            # For FCC, because schedule is length 6
            # layers = distance
            # For HCC, because schedule is length 3
            layers = 2*distance
            pre_circuit = pre_compiler.compile_to_circuit(
                code=code,
                layers=layers,
                initial_states=initial_states,
                final_measurements=final_measurements,
                observables=observables)
            pre_circuit.add_idling_noise(pre_compiler.noise_model.idling)
            M = pre_circuit.number_of_instructions(['MZ', 'MX', 'MY'])
            Q = pre_circuit.number_of_instructions(['PAULI_CHANNEL_1', 'PAULI_CHANNEL_2'])
            print(f'M, Q = {(M, Q)}')
            for p in ps:
                if bias == math.inf:
                    m = (p * (M + Q)) / M
                    q = 0
                else:
                    q = (p * (M + Q)) / (bias * M + Q)
                    m = q * bias
                print(f'p, m, q = {(p, m, q)}')
                stim_circuit = load_or_create_stim_circuit(
                    m,
                    q,
                    syndrome_extractor,
                    code=code,
                    layers=layers,
                    initial_states=initial_states,
                    final_measurements=final_measurements,
                    observables=observables)
                tasks[bias].append(sinter.Task(
                    circuit=stim_circuit,
                    json_metadata={
                        'distance': distance,
                        'bias': bias,
                        'p': p,
                        'q': q,
                        'm': m}))
    return tasks


def main():
    # Collect the samples (takes a few minutes).
    code_constructor = HoneycombCode
    bias_tasks = get_bias_tasks(code_constructor)
    for bias, tasks in bias_tasks.items():
        samples = sinter.collect(
            tasks=tasks,
            hint_num_tasks=len(tasks),
            num_workers=8,
            max_shots=10000,
            max_errors=1000,
            decoders=['pymatching'],
            print_progress=True)

        # Save samples as CSV data.
        filename = 'Tic_tac_toe_measurement_bias'
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
            group_func=lambda stat: f"{code_constructor.__name__}, d={stat.json_metadata['distance']}",
            x_func=lambda stat: stat.json_metadata['p'])

        ax.loglog()
        ax.set_ylim(1e-5, 1)
        ax.grid()
        ax.set_title(f'Measurement Bias = {bias}: Logical vs Physical Error Rate')
        ax.set_ylabel('Logical Error Rate')
        ax.set_xlabel('Circuit-Level Noise Model Parameter p')
        ax.legend()

        # Save to file and also open in a window.
        fig.savefig(f'{filename}.png')


def load_or_create_stim_circuit(
        m,
        q,
        syndrome_extractor,
        code,
        layers,
        initial_states,
        final_measurements,
        observables):
    # Save time by saving these circuits locally.
    noise_params = (q, None, q, q, m)
    hash_fields = (type(code).__name__, code.distance, layers, noise_params)
    hash_input = str(hash_fields).encode('UTF-8')
    hashed = int(hashlib.md5(hash_input).hexdigest(), 16)
    filepath = output_path() / f"stim_circuits/{hashed}.stim"
    if filepath.is_file():
        stim_circuit = stim.Circuit.from_file(filepath)
    else:
        noise_model = CircuitLevelNoise(q, None, q, q, m)
        compiler = AncillaPerCheckCompiler(
            noise_model, syndrome_extractor)
        stim_circuit = compiler.compile_to_stim(
            code=code,
            layers=layers,
            initial_states=initial_states,
            final_measurements=final_measurements,
            observables=observables)
        stim_circuit.to_file(filepath)
    return stim_circuit


def plot_thresholds_vs_bias():
    fig, ax = plt.subplots(1, 1)
    ax.set_title(f'Threshold vs Measurement Noise Bias')
    ax.set_ylabel('Threshold')
    ax.set_xlabel('Measurement Noise Bias')
    # ax.set_xscale('log', base=2)

    biases = [0, 1/8, 1/4, 1/2, 1, 2, 4, 8]
    fcc_thresholds = [
        0.0056,
        0.0055,
        0.0054,
        0.0053,
        0.0049,
        0.0046,
        0.0044,
        0.0042]
    hcc_thresholds = [
        0.0047,
        0.0046,
        0.0044,
        0.00415,
        0.00375,
        0.0032,
        0.00275,
        0.0022]

    ax.plot(biases, fcc_thresholds, label='FloquetColourCode', marker='o')
    ax.plot(biases, hcc_thresholds, label='HoneycombCode', marker='o')
    ax.legend()
    plt.show()

    filename = 'Tic_tac_toe_measurement_bias_comparison'
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{output_path()}/{filename}_{now}'
    Path(Path(filename).parent).mkdir(parents=True, exist_ok=True)
    fig.savefig(f'{filename}.png')

    # ax.xaxis.set_major_locator(MultipleLocator(1))
    # # Format the ticklabel to be 2 raised to the power of `x`
    # ax.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: int(2 ** (x-3))))


# NOTE: This is actually necessary! If the code inside 'main()' was at the
# module level, the multiprocessing children spawned by sinter.collect would
# also attempt to run that code.
if __name__ == '__main__':
    main()


# def threshold_fit(variables, B0, B1, B2, mu, pth):
#     p, L = variables
#     B0 + B1*(p-pth)*pow(L, 1/mu) + B2*pow((p-pth) * pow(L, 1/mu), 2)
# #
# popt, pcov = curve_fit(
#     threshold_fit,
#     (per_data, distance_data),
#     ler_data,
#     sigma=ler_eb_data,
#     maxfev=5000)
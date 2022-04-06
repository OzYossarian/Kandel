# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from sre_parse import State
from main.Circuit import Circuit
from main.building_blocks.Qubit import Qubit
from main.codes.RepetitionCode import RepetitionCode
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.enums import State
from main. Compiler import Compiler
from main.building_blocks.Pauli import Pauli, PauliX, PauliY, PauliZ
import stim
from main.printing.Printer2D import Printer2D
from IPython.display import Image


# ### Create a QPU

from IPython.display import Image
test_qpu = SquareLatticeQPU((6, 2))
printer = Printer2D(scale_factor=50)
printer.print_qpu(test_qpu, 'small_18_qpu')
Image(url="../output/small_18_qpu_round_0.jpg")  # , width=400, height=400)


# ### Place error correction code on QPU

rep_code = RepetitionCode(2)
test_qpu.embed(rep_code, (0, 0), 0)
printer = Printer2D(scale_factor=50)
printer.print_qpu(test_qpu, 'small_18_rep_code_qpu')
# , width=400, height=400)
Image(url="../output/small_18_rep_code_qpu_round_0.jpg")

# ### Compile the repetition code to stim

# +
test_compiler = Compiler()

test_compiler.compile_code(
    rep_code, n_code_rounds=3, measure_data_qubits=True)
circuit = Circuit()
circuit.to_stim(test_compiler.gates_at_timesteps)
print(circuit.stim_circuit)

# -

# ### Simulate the stim circuit

# +
sampler = circuit.stim_circuit.compile_detector_sampler()
print(sampler.sample(shots=10))


# -

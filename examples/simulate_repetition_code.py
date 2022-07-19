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

from main.compiling.Circuit import Circuit
from main.codes.RepetitionCode import RepetitionCode
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.compiling.compilers.Compiler import Compiler
from main.compiling.syndrome_extraction.controlled_gate_orderers.TrivialOrderer import (
    TrivialOrderer,
)
from main.compiling.syndrome_extraction.extractors.SyndromeExtractor import (
    SyndromeExtractor,
)
from main.printing.Printer2D import Printer2D

# ### Create a QPU

from IPython.display import Image

test_qpu = SquareLatticeQPU((6, 2))
printer = Printer2D(scale_factor=50)
printer.print_qpu(test_qpu, "small_18_qpu")
Image(url="../output/small_18_qpu_round_0.jpg")  # , width=400, height=400)


# ### Place error correction code on QPU

rep_code = RepetitionCode(2)
test_qpu.embed(rep_code, (0, 0), 0)
printer = Printer2D(scale_factor=50)
printer.print_qpu(test_qpu, "small_18_rep_code_qpu")
# , width=400, height=400)
Image(url="../output/small_18_rep_code_qpu_round_0.jpg")

# ### Compile the repetition code to stim

# +

syndrome_extractor = SyndromeExtractor(TrivialOrderer())
test_compiler = Compiler(noise_model=None, syndrome_extractor=syndrome_extractor)

stim_circuit = test_compiler.compile_code(rep_code, layers=3, perfect_final_layer=True)
print(stim_circuit)

# -

# ### Simulate the stim circuit

# +
sampler = stim_circuit.compile_detector_sampler()
print(sampler.sample(shots=10))


# -

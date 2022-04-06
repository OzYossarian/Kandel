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

from IPython.display import Image
from sre_parse import State
from main.Circuit import Circuit
from main.building_blocks.Qubit import Qubit
from main.codes.RotatedSurfaceCode import RotatedSurfaceCode
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.enums import State
from main. Compiler import Compiler
from main.printing.Printer2D import Printer2D


# ### Create a QPU
#

test_qpu = SquareLatticeQPU((20, 20))
printer = Printer2D(scale_factor=50)
printer.print_qpu(test_qpu, '20_20_qpu')
Image(url="../output/20_20_qpu_round_0.jpg")  # , width=400, height=400)


# ### Place error correction code on QPU

d7_surface_code = RotatedSurfaceCode(3)
test_qpu.embed(d7_surface_code, (0, 0), (0,1))
printer = Printer2D(scale_factor=50)
printer.print_qpu(test_qpu, 'small_2_rep_code_d72_qpu')
Image(url= "../output/small_2_rep_code_d72_qpu_round_0.jpg")#, width=400, height=400)





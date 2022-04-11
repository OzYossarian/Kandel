from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.codes.FloquetColourCode import FloquetColourCode
from main.codes.HoneycombCode import HoneycombCode
from main.codes.ToricColourCode import ToricColourCode
from main.codes.TriangularColourCode import TriangularColourCode
from main.printing.Printer2D import Printer2D


def print_code():
    printer = Printer2D(scale_factor=50)
    qpu = SquareLatticeQPU((30, 20))
    # printer.print_qpu(qpu, 'empty_qpu')

    # code = TriangularColourCode(5)
    # code = HoneycombCode(4)
    code = FloquetColourCode(4)
    # code = ToricColourCode(4)
    qpu.embed(code, (0, 0), (0, 1))
    printer.print_qpu(qpu, 'fcc')


print_code()

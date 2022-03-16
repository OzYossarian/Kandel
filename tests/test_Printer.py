from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.codes.ToricColourCode import ToricColourCode
from main.codes.TriangularColourCode import TriangularColourCode
from main.enums import Layout
from main.printing.Printer2D import Printer2D


def test_print_triangular_colour_code():
    printer = Printer2D(scale_factor=50)
    qpu = SquareLatticeQPU((20, 20))
    # printer.print_qpu(qpu, 'empty_qpu')

    # colour_code = TriangularColourCode(4, Layout.Hexagonal)
    colour_code = ToricColourCode(4, Layout.Hexagonal)
    qpu.embed(colour_code, (2,2), (0,1))
    printer.print_qpu(qpu, 'colour_code')


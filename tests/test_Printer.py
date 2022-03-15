from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.codes.ColourCode import TriangularColourCode
from main.enums import Layout
from main.printing.Printer2D import Printer2D


def test_print_triangular_colour_code():
    printer = Printer2D(scale_factor=50)

    qpu = SquareLatticeQPU((13, 13))
    # printer.print_qpu(qpu, 'empty_qpu')

    colour_code = TriangularColourCode(4, Layout.Brickwork)
    qpu.embed(colour_code, (0,0), (0,1))
    printer.print_qpu(qpu, 'colour_code')


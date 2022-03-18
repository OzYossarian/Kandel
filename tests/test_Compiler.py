from main.Compiler import Compiler
from main.QPUs.SquareLatticeQPU import SquareLatticeQPU
from main.codes.RepetitionCode import RepetitionCode
from main.printing.Printer2D import Printer2D
from main.Circuit import Circuit


def test_compile_rep_code():
    test_qpu = SquareLatticeQPU((6, 1))
    rep_code = RepetitionCode(3)

    test_qpu.embed(rep_code, (0, 0), 0)
    print(test_qpu.codes[1].schedule[0][-1].operators[0])
    print(test_qpu.codes[1].schedule[0][-1])

    #print(test_qpu.codes[1].schedule[0][-1].operators[0].pauli, 'Pauli')
    test_compiler = Compiler()
    test_circuit = Circuit()
    test_compiler.compile_schedule(test_qpu, test_circuit)
    # compile(test_qpu)

#    printer = Printer2D(scale_factor=50)
#    printer.print_qpu(test_qpu, 'rep_test')


test_compile_rep_code()

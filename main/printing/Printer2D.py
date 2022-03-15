from PIL import Image

from main.Colour import Black, Colour
from main.building_blocks.Check import Check
from main.codes.Code import Code
from main.QPUs.QPU import QPU
from main.building_blocks.Qubit import Qubit
from main.printing.Printer import Printer
from main.printing.Printout import Printout
from main.utils import mid


class Printer2D(Printer):
    def __init__(self, scale_factor: int = 10):
        super().__init__(scale_factor)

    def print_qpu(self, qpu: type(QPU), filename: str):
        x_max = max(x for (x, y) in qpu.qubits)
        y_max = max(y for (x, y) in qpu.qubits)
        size = self.scale((x_max, y_max), (2, 2))
        image = Image.new('RGB', size, (255, 255, 255))
        data_qubit_diameter = self.scale_factor/10
        rounds = 1 \
            if len(qpu.codes) == 0 \
            else max(len(code.schedule) for code in qpu.codes.values())
        printouts = [Printout(image, offset=(1, 1)) for _ in range(rounds)]
        for round in range(rounds):
            printout = printouts[round]
            for code in qpu.codes.values():
                self._print_code(code, round, printout)
            # Now print all QPU qubits
            for qubit in qpu.qubits.values():
                self._print_qubit(qubit, printout, data_qubit_diameter, Black)
            printout.save(f'{filename}_round_{round}')

    def _print_code(self, code: Code, round: int, printout: Printout):
        rounds = len(code.schedule)
        checks = code.schedule[round % rounds]
        for check in checks:
            self._print_check(check, printout)

    def _print_check(self, check: Check, printout: Printout):
        # Qubits in the check must be given in 'polygonal order' - that is,
        # if we were to represent the check as a polygon as we usually do
        # (e.g. colour code, surface code) then adjacent qubits in the list
        # of keys of 'check.operators' should be adjacent in this polygon.
        weight = len(check.operators)
        if weight == 1:
            qubit = check.operators[0].qubit
            self._print_qubit(qubit, printout, self.scale_factor / 2, Black)
        if weight == 2:
            self._print_weight_2_check(check, printout)
        else:
            self._print_higher_weight_check(check, printout, weight)

    def _print_weight_2_check(self, check: Check, printout: Printout):
        ops = check.operators  # Quick shorthand
        midpoint = mid(ops[0].qubit.coords, ops[1].qubit.coords)
        midpoint = self.scale(midpoint, printout.offset)
        for i in [0, 1]:
            colour = check.colour \
                if check.colour is not None \
                else ops[i].pauli.colour
            endpoint = self.scale(ops[i].qubit.coords, printout.offset)
            line = (endpoint, midpoint)
            printout.draw.line(line, colour.rgb, self.scale_factor // 4)

    def _print_higher_weight_check(self, check: Check, printout: Printout, weight: int):
        ops = check.operators  # Quick shorthand
        mid_next = mid(ops[0].qubit.coords, ops[-1].qubit.coords)
        for i in range(weight):
            mid_last = mid_next
            mid_next = mid(ops[i].qubit.coords, ops[(i + 1) % weight].qubit.coords)
            polygon = (check.center, mid_last, ops[i].qubit.coords, mid_next)
            polygon = tuple(
                self.scale(coords, printout.offset)
                for coords in polygon)
            colour = check.colour \
                if check.colour is not None \
                else ops[i].pauli.colour
            printout.draw.polygon(polygon, colour.rgb)

    def _print_qubit(self, qubit: Qubit, printout: Printout,
                     diameter: float, colour: Colour):
        (x, y) = self.scale(qubit.coords, printout.offset)
        min = (x - diameter / 2, y - diameter / 2)
        max = (x + diameter / 2, y + diameter / 2)
        printout.draw.ellipse((min, max), colour.rgb)

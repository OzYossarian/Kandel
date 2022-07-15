from PIL import Image

from main.Colour import Black, Colour, White
from main.building_blocks.Check import Check
from main.codes.Code import Code
from main.QPUs.QPU import QPU
from main.building_blocks.Qubit import Qubit
from main.printing.Printer import Printer
from main.printing.Printout import Printout
from main.utils.utils import mid


class Printer2D(Printer):
    def __init__(self, scale_factor: int = 20):
        super().__init__(scale_factor)

    def print_qpu(self, qpu: type(QPU), filename: str):
        x_max = max(x for (x, y) in qpu.qubits)
        y_max = max(y for (x, y) in qpu.qubits)
        size = self.scale((x_max, y_max), (2, 2))
        data_qubit_diameter = self.scale_factor/10

        # Make a separate printout for each 'round' of the QPU - e.g. Floquet
        # codes measure different stabilizers in each round.
        rounds = 1 \
            if len(qpu.codes) == 0 \
            else max(code.schedule_length for code in qpu.codes.values())
        printouts = [
            Printout(Image.new('RGB', size, White.rgb), offset=(1, 1))
            for _ in range(rounds)]

        for round in range(rounds):
            printout = printouts[round]
            # Print each code currently embedded in the QPU.
            for code in qpu.codes.values():
                self._print_code(code, round, printout)
            # Now print all other QPU qubits.
            for qubit in qpu.qubits.values():
                self._print_qubit(qubit, printout, data_qubit_diameter, Black)
            printout.save(f'{filename}_round_{round}')

    def _print_code(self, code: Code, round: int, printout: Printout):
        # TODO - print code without embedding on a QPU.
        checks = code.check_schedule[round % code.schedule_length]
        for check in checks:
            self._print_check(check, printout)

    def _print_check(self, check: Check, printout: Printout):
        # Qubits in the check must be given in 'polygonal order' - that is,
        # if we were to represent the check as a polygon as we usually do
        # (e.g. colour code, surface code) then adjacent qubits in the list
        # of keys of 'check.paulis' should be adjacent in this polygon.
        weight = len(check.paulis)
        if weight == 1:
            qubit = check.paulis[0].qubit
            self._print_qubit(qubit, printout, self.scale_factor / 2, Black)
        if weight == 2:
            self._print_weight_2_check(check, printout)
        else:
            self._print_higher_weight_check(check, printout, weight)

    def _print_weight_2_check(self, check: Check, printout: Printout):
        paulis = check.paulis  # Quick shorthand
        midpoint = mid([paulis[0].qubit.coords, paulis[1].qubit.coords])
        midpoint = self.scale(midpoint, printout.offset)
        anchor = self.scale(check.anchor, printout.offset)

        if midpoint == anchor:
            # We're going to end up drawing a line to represent this check
            def draw(line, rgb):
                printout.draw.line(line, rgb, self.scale_factor // 4)
        else:
            # We're going to draw two triangles to represent this check
            def draw(polygon, rgb):
                printout.draw.polygon(polygon, rgb)

        for i in [0, 1]:
            colour = check.colour \
                if check.colour is not None \
                else paulis[i].letter.colour
            qubit_coords = self.scale(paulis[i].qubit.coords, printout.offset)
            # Polygon will be a line if anchor and midpoint are the same.s
            polygon = tuple({anchor, qubit_coords, midpoint})
            draw(polygon, colour.rgb)

    def _print_higher_weight_check(self, check: Check, printout: Printout, weight: int):
        paulis = check.paulis  # Quick shorthand
        mid_next = mid([paulis[0].qubit.coords, paulis[-1].qubit.coords])
        for i in range(weight):
            mid_last = mid_next
            mid_next = mid([
                paulis[i].qubit.coords,
                paulis[(i + 1) % weight].qubit.coords])
            polygon = (check.anchor, mid_last, paulis[i].qubit.coords, mid_next)
            polygon = tuple(
                self.scale(coords, printout.offset)
                for coords in polygon)
            colour = check.colour \
                if check.colour is not None \
                else paulis[i].letter.colour
            printout.draw.polygon(polygon, colour.rgb)

    def _print_qubit(self, qubit: Qubit, printout: Printout,
                     diameter: float, colour: Colour):
        (x, y) = self.scale(qubit.coords, printout.offset)
        min = (x - diameter / 2, y - diameter / 2)
        max = (x + diameter / 2, y + diameter / 2)
        printout.draw.ellipse((min, max), colour.rgb)

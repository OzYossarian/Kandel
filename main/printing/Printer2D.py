from typing import List, Tuple

from PIL import Image

from main.utils.Colour import Black, Colour, White, Grey
from main.building_blocks.Check import Check
from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.codes.Code import Code
from main.QPUs.QPU import QPU
from main.building_blocks.Qubit import Qubit
from main.printing.Printer import Printer
from main.printing.Printout import Printout
from main.utils.utils import coords_mid, coords_sum


class Printer2D(Printer):
    def __init__(self, scale_factor: int = 20):
        super().__init__(scale_factor)
        self.operator_colours = {
            'X': Colour('orange', (255, 155, 0)),
            'Y': Colour('teal', (0, 255, 185)),
            'Z': Colour('purple', (145, 0, 255))}

    def print_qpu(self, qpu: QPU, filename: str):
        data_qubit_diameter = self.scale_factor/10
        printouts = self.get_printouts(list(qpu.qubits), list(qpu.codes.values()))

        for round, printout in enumerate(printouts):
            # Print each code currently embedded in the QPU.
            for code in qpu.codes.values():
                self.print_code_round(code, round, printout)
            # Now print all other QPU qubits.
            for qubit in qpu.qubits.values():
                self._print_qubit(qubit, printout, data_qubit_diameter, Black)
            printout.save(f'{filename}_round_{round}')
        return printouts

    def print_code(
            self, code: Code, filename: str, print_logicals: bool = True, layers: int = 1):
        # Going to need to print all the data qubits
        coords = list(code.data_qubits)
        # But if code has periodic geometry, might need a slightly bigger
        # printout to represent checks nicely.
        for check in code.checks:
            coords.append(check.anchor)
            for offset in check.paulis:
                coords.append(coords_sum(check.anchor, offset))
        printouts = self.get_printouts(coords, [code], layers)

        for round, printout in enumerate(printouts):
            self.print_code_round(code, round, print_logicals, printout)
            printout.save(f'{filename}_round_{round}')
        return printouts

    def print_code_round(
            self, code: Code, round: int, print_logicals: bool,
            printout: Printout):
        # First print the checks
        if code.schedule_length != None:
            checks = code.check_schedule[round % code.schedule_length]
        else:
            checks = code.checks
        for check in sorted(checks, key=lambda check: -check.weight):
            self._print_check(check, printout)

        # Then print the data qubits on top, in case we missed any.
        for qubit in code.data_qubits.values():
            self._print_qubit(qubit, printout, self.scale_factor/3, Grey)

        # Finally, print the logical operators.
        logical_operators = [
            logical_operator
            for logical_qubit in code.logical_qubits
            for logical_operator in logical_qubit.operators
            if logical_operator is not None]
        if print_logicals and len(logical_operators) > 0:
            max_diameter = self.scale_factor
            min_diameter = self.scale_factor // 2
            decrease_per_operator = \
                (max_diameter - min_diameter) / len(logical_operators)
            for i, logical_operator in enumerate(logical_operators):
                diameter = max_diameter - i * decrease_per_operator
                self._print_operator(
                    logical_operator, round, printout, diameter)

    def _print_check(self, check: Check, printout: Printout):
        # Qubits in the check must be given in 'polygonal order' - that is,
        # if we were to represent the check as a polygon as we usually do
        # (e.g. colour code, surface code) then adjacent qubits in the list
        # of keys of 'check.paulis' should be adjacent in this polygon.
        if check.weight == 1:
            pauli = next(iter(check.paulis.values()))
            colour = check.colour \
                if check.colour is not None \
                else pauli.letter.colour
            diameter = self.scale_factor / 2
            self._print_qubit(pauli.qubit, printout, diameter, colour)
        elif check.weight == 2:
            self._print_weight_2_check(check, printout)
        else:
            self._print_higher_weight_check(check, printout)

    def _print_weight_2_check(self, check: Check, printout: Printout):
        # Find pauli locations given their relation to check anchor.
        paulis = {
            coords_sum(check.anchor, offset): pauli
            for offset, pauli in check.paulis.items()}  # Quick shorthand
        pauli_coords = list(paulis.keys())

        midpoint = coords_mid(pauli_coords[0], pauli_coords[1])
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

        for coords, pauli in paulis.items():
            colour = check.colour \
                if check.colour is not None \
                else pauli.letter.colour
            qubit_coords = self.scale(coords, printout.offset)
            # Polygon will be a line if anchor and midpoint are the same
            polygon = tuple({anchor, qubit_coords, midpoint})
            draw(polygon, colour.rgb)

    def _print_higher_weight_check(self, check: Check, printout: Printout):
        # Find pauli locations given their relation to check anchor.
        paulis = {
            coords_sum(check.anchor, offset): pauli
            for offset, pauli in check.paulis.items()}  # Quick shorthand
        pauli_coords = list(paulis.keys())

        mid_next = coords_mid(pauli_coords[0], pauli_coords[-1])
        for i in range(check.weight):
            mid_last = mid_next
            mid_next = coords_mid(
                pauli_coords[i],
                pauli_coords[(i + 1) % check.weight])
            polygon = (check.anchor, mid_last, pauli_coords[i], mid_next)
            polygon = tuple(
                self.scale(coords, printout.offset)
                for coords in polygon)
            colour = check.colour \
                if check.colour is not None \
                else list(paulis.values())[i].letter.colour
            printout.draw.polygon(polygon, colour.rgb)

    def _print_qubit(
            self, qubit: Qubit, printout: Printout, diameter: float,
            colour: Colour):
        (x, y) = self.scale(qubit.coords, printout.offset)
        min = (x - diameter / 2, y - diameter / 2)
        max = (x + diameter / 2, y + diameter / 2)
        printout.draw.ellipse((min, max), colour.rgb)

    def _print_operator(
            self, operator: LogicalOperator, round: int, printout: Printout,
            diameter: float):
        if operator is not None:
            paulis = operator.at_round(round-1)
            for pauli in paulis:
                colour = self.operator_colours[pauli.letter.letter]
                self._print_qubit(pauli.qubit, printout, diameter, colour)

    def get_printouts(
            self, coords: List[Tuple[int, int]], codes: List[Code], layers: int):
        # coords should be a list of all locations on which something will
        # be printed.
        x_max = max(x for (x, y) in coords)
        x_min = min(x for (x, y) in coords)
        y_max = max(y for (x, y) in coords)
        y_min = min(y for (x, y) in coords)
        unscaled_size = (x_max - x_min, y_max - y_min)
        buffer = (2, 2)
        # Redefine where (0,0) is
        offset = (1 - x_min, 1 - y_min)
        size = self.scale(unscaled_size, buffer)
        # Make a separate printout for each round - e.g. Floquet
        # codes measure different stabilizers in each round.
        print(max([code.schedule_length for code in codes],default=1))

        max_rounds = max([code.schedule_length for code in codes])*layers
        
        if max_rounds == None or max_rounds==0:
            rounds=1
        else:
            rounds = max_rounds
        printouts = [
            Printout(Image.new('RGB', size, White.rgb), offset)
            for _ in range(rounds)]
        return printouts

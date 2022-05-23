from main.building_blocks.Check import Check
from main.compiling.syndrome_extraction.cnot_order.CNOTOrderer import CNOTOrderer


class TrivialOrderer(CNOTOrderer):
    def __init__(self):
        super().__init__()

    def order(self, check: Check):
        # This extractor should be used in cases where it is safe to place
        # CNOTs in the order that the Paulis are listed within the check, e.g.
        # in a tic-tac-toe code, or repetition code.
        return check.paulis


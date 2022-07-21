from main.building_blocks.Check import Check
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import ControlledGateOrderer


class TrivialOrderer(ControlledGateOrderer):
    def __init__(self):
        super().__init__()

    def order(self, check: Check):
        # This extractor should be used in cases where it is safe to place
        # CNOTs in the order that the Paulis are listed within the check, e.g.
        # in a tic-tac-toe code, or repetition code.
        return list(check.paulis.values())


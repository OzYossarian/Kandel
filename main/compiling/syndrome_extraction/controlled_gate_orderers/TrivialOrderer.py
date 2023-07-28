from main.building_blocks.Check import Check
from main.compiling.syndrome_extraction.controlled_gate_orderers.ControlledGateOrderer import ControlledGateOrderer


class TrivialOrderer(ControlledGateOrderer):
    """
    This orderer just returns a check's Paulis in the same order in which
    they are stored. Useful in scenarios where it's irrelevant in which
    order controlled not gates are performed - e.g. in tic-tac-toe codes.
    """
    def __init__(self):
        super().__init__()

    def order(self, check: Check):
        return list(check.paulis.values())

    def __eq__(self, other):
        # Any two instances of a TrivialOrderer are equal!
        return type(self) == type(other)

    def __hash__(self):
        return hash(type(self))


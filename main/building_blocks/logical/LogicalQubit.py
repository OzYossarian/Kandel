
from main.building_blocks.logical.LogicalOperator import LogicalOperator


class LogicalQubit:
    def __init__(
            self,
            x: LogicalOperator = None,
            y: LogicalOperator = None,
            z: LogicalOperator = None):
        """
        Class representing a logical qubit. Defined simply by its Pauli
        operators X, Y and Z. These can be left as None if one isn't
        interested in any particular one of them.

        Args:
            x: logical X operator. Defaults to None
            y: logical Y operator. Defaults to None
            z: logical Z operator. Defaults to None
        """
        self.x = x
        self.y = y
        self.z = z

    @property
    def operators(self):
        return [self.x, self.y, self.z]

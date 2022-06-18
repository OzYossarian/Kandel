from main.building_blocks.logical.LogicalOperator import LogicalOperator


class LogicalQubit:
    def __init__(self, x: LogicalOperator, z: LogicalOperator):
        self.x = x
        self.z = z

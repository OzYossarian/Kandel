from typing import List

from main.building_blocks.logical.LogicalOperator import LogicalOperator
from main.utils.NiceRepr import NiceRepr


class LogicalQubit(NiceRepr):
    def __init__(
            self,
            x: LogicalOperator = None,
            y: LogicalOperator = None,
            z: LogicalOperator = None):
        """Class representing a logical qubit using its logical operators X, Y and Z.
        These can be left as None if one isn't interested in any particular one of them.

        Args:
            x: logical X operator. Defaults to None
            y: logical Y operator. Defaults to None
            z: logical Z operator. Defaults to None
        """
        operators = [x, y, z]
        self._assert_has_an_operator(operators)
        self._assert_operator_coords_valid(operators)
        # TODO - could check operators satisfy Pauli relations - e.g. XY = iZ,
        #  etc. But since these only need to hold up to stabilizer, isn't so
        #  trivial (means checking if an element is in a group, which isn't
        #  necessarily fast). Also here wouldn't be the place for it - would
        #  have to be on the Code object.

        self.x = x
        self.y = y
        self.z = z
        self.operators = operators

        super().__init__(['x', 'y', 'z'])

    @staticmethod
    def _assert_has_an_operator(operators: List[LogicalOperator]):
        if all([operator is None for operator in operators]):
            raise ValueError(
                "At least one operator on a logical qubit must be non-None")

    @staticmethod
    def _assert_operator_coords_valid(operators: List[LogicalOperator]):
        non_none_operators = [
            operator for operator in operators
            if operator is not None]
        dimensions = {
            operator.dimension for operator in non_none_operators}
        if len(dimensions) > 1:
            raise ValueError(
                "All operators within a logical qubit must have the same "
                f"dimensions. Instead, found dimensions {dimensions}. "
                f"Operators X, Y and Z respectively are {operators}.")
        all_tuple_coords = all([
            operator.has_tuple_coords for operator in non_none_operators])
        all_non_tuple_coords = all([
            not operator.has_tuple_coords for operator in non_none_operators])
        # Exactly one must be true
        if all_tuple_coords == all_non_tuple_coords:
            raise ValueError(
                "Either all operators within a logical qubit should have "
                "tuple coordinates, or none of them should."
                f"Operators X, Y and Z respectively are {operators}")
                
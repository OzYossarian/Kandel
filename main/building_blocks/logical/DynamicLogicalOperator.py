from typing import List, Callable
from main.building_blocks.Check import Check
from .LogicalOperator import LogicalOperator
from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.building_blocks.pauli.Pauli import Pauli


class DynamicLogicalOperator(LogicalOperator):
    def __init__(self, initial_paulis: List[Pauli], update: Callable[[int], List[Check]]):
        self._at_round = {-1: initial_paulis}
        self._products = {-1: PauliProduct(initial_paulis, identities_removed=True)}
        self._updates = {}
        self._update = update
        super().__init__(initial_paulis)
    
    def update(self, round: int) -> List[Check]:
        if round not in self._updates:
            update = self._update(round)
            self._updates[round] = update
            return update
        else:
            return self._updates[round]

    def at_round(self, round: int) -> List[Pauli]:
        if round not in self._at_round:
            t = round - 1
            while t not in self._at_round:
                # While loop will eventually terminate because -1 is always a key.
                t -= 1 
            # Found the last time we recorded the state of the logical operator.
            last_updated = t
            for t in range(last_updated + 1, round + 1):
                checks_to_multiply_in = self.update(t)
                paulis_to_multiply_in = [
                    pauli 
                    for check in checks_to_multiply_in 
                    for pauli in list(check.paulis.values())]
                new_product_paulis = paulis_to_multiply_in + self._products[t-1].paulis
                product = PauliProduct(new_product_paulis, identities_removed=True)
                self._products[t] = product
                self._at_round[t] = product.paulis
        return self._at_round[round]

    
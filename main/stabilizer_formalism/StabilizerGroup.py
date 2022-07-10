from typing import List

from main.building_blocks.pauli.PauliProduct import PauliProduct
from main.building_blocks.pauli.utils import commutes, compose


class StabilizerGroup:
    def __init__(self, generators: List[PauliProduct]):
        self.generators = generators

    def measure(self, pauli_products: List[PauliProduct]):
        for pauli_product in pauli_products:
            anti_commuters = [
                generator for generator in self.generators
                if not commutes(pauli_product, generator)]
            if len(anti_commuters) > 0:
                # Need to remove one of these anti-commuting generators, and
                # multiplying it to the other anti-commuting generators (if
                # any exist).
                for anti_commuter in anti_commuters:
                    self.generators.remove(anti_commuter)
                updated_generators = [
                    compose(anti_commuter.paulis + anti_commuters[0].paulis)
                    for anti_commuter in anti_commuters[1:]]
                # Sort by coords just for niceness.
                updated_generators = [
                    PauliProduct(sorted(generator, key=lambda g: g.qubit.coords))
                    for generator in updated_generators]
                self.generators.extend(updated_generators)
            # Now add the new pauli product into the generating set.
            self.generators.append(pauli_product)
            # Then just repeat this for every new pauli product.

    def commutes(self, pauli_product: PauliProduct):
        # Returns whether the given pauli product commutes with all of the
        # generators (if yes, it commutes with the entire group).
        return all([
            commutes(pauli_product, generator)
            for generator in self.generators])

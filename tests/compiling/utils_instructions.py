from typing import List, Tuple, Any

import stim

from main.building_blocks.Qubit import Qubit


class MockInstruction:
    """
    This class exists only for testing. It allows us to use the built-in
    `==` equality comparison between MockInstructions and actual Instructions.
    This gets around the fact that just implementing __eq__ on the
    Instruction class causes issues, because Instructions are used as keys
    to a dictionary in the Measurer. Indeed, this is how the Measurer
    remembers which measurements measure which checks in which round.
        Perhaps there's a better design that just lets us implement __eq__
    on Instructions! But it looks to me like that would force us to
    make the Circuit class know about 'rounds' of a QEC code, which I'm
    not keen on. TODO - think about this more!
    """
    def __init__(
            self, qubits: List[Qubit], name: str,
            params: Tuple[float, ...] = (), is_measurement: bool = False,
            is_noise: bool = False, targets: List[stim.GateTarget] = None):
        self.qubits = qubits
        self.name = name
        self.params = params
        self.is_measurement = is_measurement
        self.is_noise = is_noise
        self.targets = targets

    def __eq__(self, other: Any):
        # Order within the lists of qubits matters here, so for once we
        # really should use list comparison in this equality function.
        # But note crucially we don't check that types are the same.
        return \
            self.qubits == other.qubits and \
            self.name == other.name and \
            self.params == other.params and \
            self.is_measurement == other.is_measurement and \
            self.is_noise == other.is_noise and \
            self.targets == other.targets

    def __hash__(self):
        targets = None if self.targets is None else tuple(self.targets)
        return hash((
            tuple(self.qubits),
            self.name,
            self.params,
            self.is_measurement,
            self.is_noise,
            targets))

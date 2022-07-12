from typing import List, Tuple

import stim

from main.building_blocks.Qubit import Qubit
from main.utils.DebugFriendly import DebugFriendly


class Instruction(DebugFriendly):
    def __init__(
            self, qubits: List[Qubit], name: str,
            params: Tuple[float, ...] = (), is_measurement: bool = False,
            is_noise: bool = False, targets: List[stim.GateTarget] = None):
        # Order within 'qubits' matters - e.g. if this is a CNOT gate, order
        # tells us which is the control (element 0) and which is the target
        # (element 1).
        #   Important - 'targets' should ONLY be overwritten if we want the
        # usual code for generating the targets to be overwritten. e.g. For
        # Pauli product measurement, the syntax of the stim instruction is
        # different to the usual one.
        self.qubits = qubits
        self.name = name
        self.params = params
        self.is_measurement = is_measurement
        self.is_noise = is_noise
        self.targets = targets
        # TODO - add a 'duration' attribute and adjust idling noise
        #  accordingly

        repr_keys = ['name', 'params', 'qubits']
        if self.targets is not None:
            repr_keys.append('targets')
        super().__init__(repr_keys)



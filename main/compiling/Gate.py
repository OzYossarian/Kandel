from typing import List, Tuple

from main.building_blocks.Qubit import Qubit
from main.utils.DebugFriendly import DebugFriendly


class Gate(DebugFriendly):
    def __init__(
            self, qubits: List[Qubit], name: str,
            params: Tuple[float, ...] = (), is_measurement : bool = False,
            is_noise : bool = False):
        # Order within 'qubits' matters - e.g. if this is a CNOT gate, order
        # tells us which is the control (element 0) and which is the target
        # (element 1).
        self.qubits = qubits
        self.name = name
        self.params = params
        self.is_measurement = is_measurement
        self.is_noise = is_noise
        # TODO - add a 'duration' attribute and adjust idling noise
        #  accordingly

        super().__init__(['name', 'params', 'qubits'])



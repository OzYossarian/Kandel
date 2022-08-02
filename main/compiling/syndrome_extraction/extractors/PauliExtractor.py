from typing import Iterable


class PauliExtractor:
    def __init__(
            self, pre_rotations: Iterable[str], controlled_gate: str,
            ancilla_is_control: bool, post_rotations: Iterable[str]):
        self.pre_rotations = pre_rotations
        self.controlled_gate = controlled_gate
        self.ancilla_is_control = ancilla_is_control
        self.post_rotations = post_rotations

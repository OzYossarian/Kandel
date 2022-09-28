from typing import Iterable


class PauliExtractor:
    def __init__(
            self, pre_rotations: Iterable[str], controlled_gate: str,
            ancilla_is_control: bool, post_rotations: Iterable[str]):
        """
        A small helper class to collect together data needed when processing
        individual Paulis during a syndrome extraction routine.
        Args:
            pre_rotations:
                Names of any gates to perform on the given data qubit before
                the controlled gate.
            controlled_gate:
                Name of the controlled gate to perform between data and
                ancilla qubit.
            ancilla_is_control:
                Whether the ancilla is the control qubit or target qubit in
                the controlled gate implementation.
            post_rotations:
                Names of any gates to perform on the given data qubit
                immediately after the controlled gate.
        """
        self.pre_rotations = pre_rotations
        self.controlled_gate = controlled_gate
        self.ancilla_is_control = ancilla_is_control
        self.post_rotations = post_rotations

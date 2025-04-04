from typing import List, Tuple

import stim

from main.building_blocks.Qubit import Qubit
from main.utils.NiceRepr import NiceRepr


class Instruction(NiceRepr):
    def __init__(
            self, qubits: List[Qubit], name: str,
            params: Tuple[float, ...] = (), is_measurement: bool = False,
            is_noise: bool = False, targets: List[stim.GateTarget] = None):
        """

        Args:
            qubits:
                The qubits involved in this instruction. Note that order
                matters - e.g. if this instruction represents a CNOT gate,
                the control is the qubit at index 0 in `qubits`, while the
                target has index 1.
            name:
                The name of this instruction, as recognised by Stim
            params:
                Parameters for this instruction, if needed.
                Defaults to ().
            is_measurement:
                Whether this instruction represents a measurement.
                Defaults to False.
            is_noise:
                Whether this instruction represents a noise channel.
                Defaults to False.
            targets:
                The Stim targets for this instruction. Should only be given
                if one wants the usual code for generating the targets to be
                overwritten. Defaults to None. Note: this ISN'T how Pauli 
                product measurements are done - we need the qubit indices 
                as part of their targets, which we don't have access to til 
                compiling a Circuit to a stim.Circuit much later.
        """
        self._assert_qubits_valid(qubits)

        self.qubits = qubits
        self.name = name
        self.params = params
        self.is_measurement = is_measurement
        self.is_noise = is_noise
        self.targets = targets
        # TODO - if targets is not None, should we check that its length is
        #  equal to the qubit length?
        # TODO - add a 'duration' attribute and adjust idling noise
        #  accordingly

        repr_keys = ['name', 'params', 'qubits']
        if self.targets is not None:
            repr_keys.append('targets')
        super().__init__(repr_keys)

    @staticmethod
    def _assert_qubits_valid(qubits: List[Qubit]):
        if len(qubits) == 0:
            raise ValueError(
                f"An instruction must apply to at least one qubit!")
        if len(set(qubits)) != len(qubits):
            raise ValueError(
                f"Can't include the same qubit more than once in an "
                f"instruction! Qubits given are: {qubits}")
        # TODO - also check dimensions are all the same?
        #  And either all have tuple coords or all have non-tuple coords?

from typing import Tuple
from main.enums import State


Coordinates = Tuple[int, ...] | int


class Qubit(object):
    def __init__(self, position: Coordinates, initial_state: State):
        self.position = position
        self.initial_state = initial_state

    def __repr__(self):
        return(f"position={self.position},state=|{self.initial_state.value}>")

    def __eq__(self, other):
        if isinstance(other, Qubit):
            return(self.__dict__ == other.__dict__)
        return(False)

    def __hash__(self):
        return(object.__hash__(self))

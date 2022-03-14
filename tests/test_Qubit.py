from main.Qubit import Qubit
from main.enums import State


def test_eq():
    assert Qubit(1, State.Zero) == Qubit(1, State.Zero)
    assert Qubit(2, State.Zero) != Qubit(1, State.Zero)
    assert Qubit(1, State.Zero) != Qubit(1, State.One)

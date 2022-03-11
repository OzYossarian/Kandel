from main.Qubit import Qubit


def test_eq():
    assert Qubit((1), 0) == Qubit((1), 0)

import random
from collections import Counter

from main.utils.NiceRepr import NiceRepr
from main.utils.utils import modulo_duplicates


class TestDebugFriendly(NiceRepr):
    def __init__(self, something):
        self.something = something
        super().__init__(['something'])


def test_debug_friendly():
    text = 'some string'
    obj = TestDebugFriendly(text)
    assert str(obj) == "{'something': 'some string'}"


def test_modulo_duplicates():
    # Construct some random list of integers, apply the 'mod duplicates'
    # method, and check it worked. Repeat several times.
    pass
repeat = 100
for i in range(repeat):
    list_range = random.randint(1, 100)
    list_size = random.randint(1, 100)
    xs = random.choices(range(0, list_range), k=list_size)
    unique = set(xs)
    x_counts = Counter(xs)
    for j in range(1, list_size):
        ys = modulo_duplicates(xs, j)
        y_counts = Counter(ys)
        assert all(
            y_counts[item] == (x_counts[item] % j)
            for item in unique)

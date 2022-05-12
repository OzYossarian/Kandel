from main.utils.DebugFriendly import DebugFriendly


class TestDebugFriendly(DebugFriendly):
    def __init__(self, something):
        self.something = something
        super().__init__(['something'])


def test_debug_friendly():
    text = 'some string'
    obj = TestDebugFriendly(text)
    assert str(obj) == "{'something': 'some string'}"


def test_modulo_duplicates():
    assert False

from main.utils import DebugFriendly


class TestDebugFriendly(DebugFriendly):
    def __init__(self, something):
        self.something = something
        self.something_else = 42


def test_debug_friendly():
    text = 'some_string'
    obj = TestDebugFriendly(text)
    assert str(obj) == f"{{'something': '{text}', 'something_else': 42}}"
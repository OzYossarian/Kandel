from main.utils import DebugFriendly


class TestDebugFriendly(DebugFriendly):
    def __init__(self, something):
        self.something = something
        super().__init__(['something'])


def test_debug_friendly():
    text = 'some_string'
    obj = TestDebugFriendly(text)
    assert str(obj) == f"{{\n    \"something\": \"{text}\"\n}}"

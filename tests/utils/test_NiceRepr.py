from typing import Any

from main.utils.NiceRepr import NiceRepr


class Wrapper:
    def __init__(self, contents: Any):
        self.contents = contents


class MockNiceRepr(NiceRepr):
    def __init__(self, something):
        self.something = something
        self.wrapped = Wrapper('anything')
        self.double_wrapped = Wrapper(Wrapper(0))
        self.dictionary = {
            'a': 0,
            'b': 1}
        super().__init__([
            'something',
            'wrapped.contents',
            'double_wrapped.contents.contents',
            'dictionary.b'])


def test_nice_repr():
    text = 'some string'
    obj = MockNiceRepr(text)
    assert str(obj) == str({
        'something': 'some string',
        'wrapped.contents': 'anything',
        'double_wrapped.contents.contents': 0,
        'dictionary.b': 1})


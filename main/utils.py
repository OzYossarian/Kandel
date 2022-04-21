import json
from jsbeautifier import beautify, default_options
from json import JSONEncoder
from numbers import Number
from statistics import mean
from typing import List, Tuple, Any
from pathlib import Path


class DebugFriendlyEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, DebugFriendly):
            return o.relevant()
        try:
            return o.__dict__
        except:
            return repr(o)


class DebugFriendly:
    def __init__(self, repr_keys: List):
        """Small base class to make it easy to set up nice string
        representations of classes.

        Args:
            repr_keys: names of the important class attributes. These will
            be the only attributes included in the string representation of
            such a class instance.
        """
        self.repr_keys = repr_keys

    def __repr__(self):
        return beautify(
            json.dumps(self, cls=DebugFriendlyEncoder), default_options())

    def relevant(self):
        return {key: vars(self)[key] for key in self.repr_keys}


def output_path() -> Path:
    root = Path(__file__).parent.parent
    output = Path(root, 'output')
    return output


def mid(a: Tuple[int, ...], b: Tuple[int, ...]) -> Tuple[Number, ...]:
    return tuple(map(mean, zip(a, b)))


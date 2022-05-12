from typing import List


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
        return str(self.relevant())

    def relevant(self):
        return {key: vars(self)[key] for key in self.repr_keys}

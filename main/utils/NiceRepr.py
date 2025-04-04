from typing import List


class NiceRepr:
    def __init__(self, repr_keys: List[str]):
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
        result = {}
        for key in self.repr_keys:
            parts = key.split('.')
            item = vars(self)[parts[0]]
            for part in parts[1:]:
                item = vars(item)[part] \
                    if hasattr(item, '__dict__') \
                    else item[part]
            result[key] = item
        return result

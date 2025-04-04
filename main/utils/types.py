from typing import Tuple, Union
#mport typing

Tick = int
# TODO - allow complex numbers too! Would need to adapt some methods -
#  e.g. finding mean of coordinates using statistics.mean would break.

Coordinates = Union[Tuple[Union[int , float], ...] , int , float]

# Putting simple type aliases in their own file to avoid having to avoid circular
# imports when type hinting.
# TODO - put the rest here!

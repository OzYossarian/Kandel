from typing import Tuple


Tick = int
# TODO - allow complex numbers too! Would need to adapt some methods -
#  e.g. finding mean of coordinates using statistics.mean would break.
Coordinates = Tuple[int | float, ...] | int | float

# Putting simple type aliases in their own file to avoid having to avoid circular
# imports when type hinting.
# TODO - put the rest here!

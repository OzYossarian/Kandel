from typing import List, Tuple

from main.codes.ThreeColourableCode import ThreeColourableCode


class HexagonalCode(ThreeColourableCode):
    """
    Base class for any code that lives on a honeycomb lattice.
    We define the honeycomb lattice to be the set of all points (x, y)
    where x and y are EVEN integers satisfying (x + y) % 4 == 2.

    On such a lattice, a tessellation of hexagons can be drawn.
    We consider only the tessellation that has hexagons centred at points
    (x, y) satisfying:
        x % 6 == 4, and
        y % 4 == (2 if x % 12 == 4 else 0)

    Note: we will use the terms hexagons and plaquettes interchangeably
    in this class. Likewise anchors and centers.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def get_neighbour_coords(coords: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Given any 2D coordinate on a honeycomb lattice, this returns its
        six nearest neighbours' coordinates.
            Note further that it returns these coordinates in 'polygonal'
        order; i.e. such that two coordinates adjacent in this list would be
        adjacent corners if a hexagon were drawn centred at `coords`.

        Args:
            coords: the coordinates whose neighbours should be found

        Returns:
            list of six neighbours' coordinates, in polygonal order.
        """
        (x, y) = coords
        return [
            (x + 4, y),
            (x + 2, y + 2),
            (x - 2, y + 2),
            (x - 4, y),
            (x - 2, y - 2),
            (x + 2, y - 2)]

    @staticmethod
    def is_plaquette_column(x_coord: int):
        """
        In the honeycomb lattice and hexagonal tessellation defined here,
        every third column of coordinates contains only plaquette centers
        (i.e. contains no plaquette corners). We call such a column a
        'plaquette column'.

        Args:
            x_coord: distance along the x-axis to consider

        Returns:
            Whether the column at this point on the x-axis contains only
            plaquette centers.
        """
        return (x_coord - 4) % 6 == 0

    @staticmethod
    def is_shifted_column(x_coord: int):
        """
        In the honeycomb tessellation we define here, we can consider
        columns of hexagons. In order for these columns to tessellate
        together, every other column must be shifted vertically by (0, 2).
        We thus consider every 'odd' column of plaquettes to be 'shifted'.
        Following from this idea, we define every column of coordinates
        (x, y) satisfying x % 12 in {8, 10, 12} to be 'shifted' (a picture
        helps to explain this!).

        This method then returns whether an x-coordinate lies in such a
        'shifted' column.

        Args:
            x_coord: X-coordinate being considered.

        Returns:
            Whether this coordinate lies in a 'shifted' column.
        """
        return x_coord % 12 in [8, 10, 0]

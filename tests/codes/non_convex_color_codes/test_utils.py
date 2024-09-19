from main.codes.non_convex_color_codes.utils import *


def test_generate_triangular_lattice():
    coords_center_111 = {(3, 0, 0), (2, 1, 0), (1, 2, 0), (0, 3, 0),
                         (2, 0, 1), (0, 1, 2), (1, 0, 2), (1, 1, 1), (0, 2, 1), (0, 0, 3)}
    coords = generate_triangular_lattice(1, (1, 1, 1))
    assert coords == coords_center_111

    coords_center_333 = {(j_0+2, j_1+2, j_2+2)
                         for j_0, j_1, j_2 in coords_center_111}
    coords_333 = generate_triangular_lattice(1, (3, 3, 3))
    assert coords_333 == coords_center_333

    coords_center_313 = {(j_0+2, j_1, j_2+2)
                         for j_0, j_1, j_2 in coords_center_111}
    coords_313 = generate_triangular_lattice(1, (3, 1, 3))
    print(coords_313)
#    coords_333 = generate_triangular_lattice(1, (3, 3, 3))
#   assert coords_333 == coords_center_333

    coords_upside_down = generate_triangular_lattice(1, (1, 1, 1), True)
#    print(coords_upside_down)

    assert coords_upside_down == {(0, 2, 1), (-1, 2, 2), (1, 2, 0), (2, 1, 0),
                                  (2, -1, 2), (2, 0, 1), (2, 2, -1), (0, 1, 2), (1, 0, 2), (1, 1, 1)}


test_generate_triangular_lattice()

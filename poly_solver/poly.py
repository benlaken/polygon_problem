import copy
from random import choice
import shapely.geometry as geometry

def random_vertex(rows, columns):
    """Return a random vertex from an avaiable list of choices,
    and, after selecting one, remove it from future selection."""
    random_row = choice(rows)
    tmp_rows = copy.deepcopy(rows)
    tmp_rows.remove(random_row)
    random_column = choice(columns)
    tmp_columns = copy.deepcopy(columns)
    tmp_columns.remove(random_column)
    return (random_row, random_column), tmp_rows, tmp_columns


def random_triangle(rows, columns, try_limit=10):
    """Obtain coordinates for a starting shape from a grid of n x n,
    for the simplest valid ploygon: a triangle"""
    area = 0.0
    i = 0
    while area <= 0.0:
        i += 1
        if i > try_limit:
            raise AssertionError("Couldn't find a triangle in {0} attempts.".format(try_limit))
        coordinates = []
        while len(coordinates) < 3:
            vertex, rows, columns = random_vertex(rows, columns)
            coordinates.append(vertex)
            coordinates = list(set(coordinates)) # Ensure unique points only
        tmp_poly = geometry.Polygon(coordinates)
        area = tmp_poly.area
    return coordinates, rows, columns


def slope_of_vertexes(vertex1, vertex2, report=False):
    """Slope between two xy pairs, calculated as y2-y1/x2-x1"""
    try:
        slope = (vertex2[1] - vertex1[1])/(vertex2[0] - vertex1[0])
    except ZeroDivisionError:
        slope = 0.0
    if report:
        print("Slope between {0} and {1} is {2}".format(vertex1, vertex2, slope))
    return slope


def check_slopes(coordinates):
    """Return True if the slopes calculated from a given list of ordered coordinates
    contain no repeats, otherwise return false."""
    slope_list = []
    for i, vertex in enumerate(coordinates):
        slope_list.append(slope_of_vertexes(coordinates[i-1] ,vertex))
    assert len(coordinates) == len(slope_list), "slopes were not equal to coordinates"
    repeated_angle = len(set(slope_list)) < len(slope_list)
    if repeated_angle:
        return False
    else:
        return True


def grow_a_polygon(n):
    """Note, no point keeping track of attempted vertexs, because as the
    shape develops, a previously invalid vertex may become valid again.
    Only worth keeping track of last tried vertex?"""
    rows = list(range(1, n+1))
    columns = list(range(1, n+1))
    coordinates = None
    while not coordinates:
        try:
            coordinates, rows, columns = random_triangle(rows, columns)
        except:
            pass
    jj = 0
    while len(coordinates) < n:
        jj += 1
        if jj > 20:
            return None
        tmp_vertex, tmp_rows, tmp_columns = random_vertex(rows, columns)
        valid_shape = False
        no_slope_repeats = False
        shape_found = False
        i = 0
        while not shape_found:
            tmp_coordinates = copy.deepcopy(coordinates)
            tmp_coordinates.insert(i, tmp_vertex)
            tmp_poly = geometry.Polygon(tmp_coordinates)
            is_valid_shape = tmp_poly.is_valid
            no_slope_repeats = check_slopes(tmp_coordinates)
            if is_valid_shape and no_slope_repeats:
                rows = copy.deepcopy(tmp_rows)
                columns = copy.deepcopy(tmp_columns)
                coordinates = copy.deepcopy(tmp_coordinates)
                shape_found = True
            if i > len(coordinates):
                shape_found = True
            else:
                i += 1
    return coordinates


if __name__ == "__main__":
    cs = None
    n = 23
    while not cs:
        cs = grow_a_polygon(n)

    poly = geometry.Polygon(cs)
    print("Area:", poly.area)
    print(cs)
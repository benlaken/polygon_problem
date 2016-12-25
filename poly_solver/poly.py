import copy
from random import choice
import shapely.geometry as geometry
import sys
from tinydb import TinyDB, Query


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
            coordinates = list(set(coordinates))  # Ensure unique points only
        tmp_poly = geometry.Polygon(coordinates)
        area = tmp_poly.area
    return coordinates, rows, columns


def slope_of_vertexes(vertex1, vertex2, report=False):
    """Slope between two xy pairs, calculated as y2-y1/x2-x1"""
    try:
        slope = (vertex2[1] - vertex1[1]) / (vertex2[0] - vertex1[0])
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
        slope_list.append(slope_of_vertexes(coordinates[i - 1], vertex))
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
    rows = list(range(1, n + 1))
    columns = list(range(1, n + 1))
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
        if len(rows) > 0:
            tmp_vertex, tmp_rows, tmp_columns = random_vertex(rows, columns)
        else:
            return None
        valid_shape = False
        no_slope_repeats = False
        shape_found = False
        i = 0
        while not shape_found:
            tmp_coordinates = copy.deepcopy(coordinates)
            tmp_coordinates.insert(i, tmp_vertex)
            tmp_poly = geometry.Polygon(tmp_coordinates)
            is_valid_shape = tmp_poly.is_valid  # self-intersection comes here
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
    """
    n should be the number of vertex's and rows/columns.
    limit should be the number of random polygons to create.
    """
    Q = Query()

    path = sys.argv[0]
    n = sys.argv[1]
    try:
        int(n)
    except:
        raise ValueError("n wasn't a number")
    valid_ns = [5, 7, 11, 17, 23, 29, 37, 47, 59, 71, 83, 97, 113, 131, 149,
                167, 191, 223, 257, 293, 331, 373, 419, 467, 521]
    if n not in valid_ns:
        raise ValueError("n must be one of: {0}".format(valid_ns))
    limit = sys.argv[2]
    try:
        int(limit)
    except:
        raise ValueError("Limit wasn't a number")
    # Calculate a first polygon and use to initilise
    coords = None
    while not coords:
        coords = grow_a_polygon(n)
    poly = geometry.Polygon(coords)
    min = (poly.area, coords)
    max = (poly.area, coords)
    for r in range(limit):
        # print("Try {0}, area = {1}".format(r, poly.area))
        # print("Min = {0}, max = {1}".format(min[0], max[0]))
        # print("Min: {0}".format(min[1]))
        # print("Max: {0}".format(max[1]))
        coords = None
        while not coords:
            coords = grow_a_polygon(n)
        poly = geometry.Polygon(coords)
        # if poly.area > max[0]:
        #    max = (poly.area, coords)
        # if poly.area < min[0]:
        #    min = (poly.area, coords)
        db = TinyDB('db.json')
        result = db.search(Q.n == n)  # search open DB connection for entries of an n size
        # print(result)
        if len(result) == 0:
            # if first entry, initlise the db values:
            # print("no entry")
            db.insert({'n': n, 'max_area': poly.area,
                       'max_coordinates': coordinates,
                       'min_area': poly.area,
                       'min_coordinates': coordinates})
        elif len(result) == 1:
            # print('entry')
            if poly.area > result[0]['max_area']:
                # if a new max is found, remove old one and write new one to the db
                tmp = result[0]
                tmp['max_area'] = poly.area
                tmp['max_coordinate'] = coordinates
                db.remove(eids=[result[0].eid])
                db.insert(tmp)
            if poly.area < result[0]['min_area']:
                tmp = result[0]
                tmp['min_area'] = poly.area
                tmp['min_coordinate'] = coordinates
                db.remove(eids=[result[0].eid])
                db.insert(tmp)
        else:
            # print('More than one entry')
            raise ValueError("> 1 result found for n={} in DB file".format(n))

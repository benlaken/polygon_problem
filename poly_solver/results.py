import sys
from tinydb import TinyDB, Query


if __name__ == "__main__":
    """
    Return the details for the Database
    """
    Q = Query()
    db = TinyDB('db.json')
    #n = int(sys.argv[1])
    valid_ns = [5, 7, 11, 17, 23, 29, 37, 47, 59, 71, 83, 97, 113, 131, 149,
                167, 191, 223, 257, 293, 331, 373, 419, 467, 521]
    for n in valid_ns:
        result = db.search(Q.n == n)
        if len(result) > 0:
            result = result[0]
            print("\nFor n={0}:".format(n))
            print("min={0}, max={1}".format(result['min_area'], result['max_area']))
            print("\nmin_coordinates= {0}".format(result['min_coordinates']))
            print("\nmax_coordinates= {0}".format(result["max_coordinates"]))
            print("------------------------------------")

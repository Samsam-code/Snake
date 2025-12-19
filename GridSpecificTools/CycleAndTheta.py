"""
Some simple Hamiltonian Cycles and spanning Theta(m*n-3, 2, 2) subgraphs.
m is the short vertical edge length, first coord
n is the long horizontal edge length, second coord
"""

def find_HC(m, n):
    return [i*n+j for i, j in find_HC_coord(m, n)]

def find_theta(m, n):
    path, (hi, hj), (ahi, ahj), anti_hole_idx = find_theta_coord(m, n)
    path = [i*n+j for i,j in path]
    hole = hi * n + hj
    antihole = ahi * n + ahj
    return  path, hole, antihole, anti_hole_idx

def find_HC_coord(m, n):
    if m%2 == 0:    
        i_range = list(range(m))
        path = [(i,0) for i in i_range]
        j_range = list(range(1, n))
        for i in reversed(i_range):
            path += [(i, j) for j in j_range]
            j_range = j_range[::-1]
        return path
    else:
        j_range = list(range(n))
        path = [(0,j) for j in j_range]
        i_range = list(range(1, m))
        for j in reversed(j_range):
            path += [(i, j) for i in i_range]
            i_range = i_range[::-1]
        return path


def find_theta_coord(m, n):
    # vertical drop from (1,0)
    path = [(i,0) for i in range(1, m)]

    # haircomb until (2, n-1)
    j_range = list(range(1, n))
    for i in range(m-1, 1, -1):
        path += [(i,j) for j in j_range]
        j_range = j_range[::-1]

    # finally, wiggles filling top two rows avoiding (0,0)
    for j in range(n-1, 0, -2):
        path += [(1, j), (0,j), (0, j-1), (1, j-1)]

    hole = (0,0)
    antihole = (1,1)
    antihole_idx = m*n-2
    return path, hole, antihole, antihole_idx


# TO DO: update this to integer labelling.
def find_coil_HC(m, n):
    
    loop = []
    if m % 2 == 0:
        width = n // 2
        # down left side
        j_range = list(range(width))
        for i in range(1, m-1):
            loop += [(i,j) for j in j_range]
            j_range = j_range[::-1]
        loop += [(m-1, j) for j in range(n)]
        # up right side
        j_range = list(range(n-1, width-1, -1))
        for i in range(m-2, 0, -1):
            loop += [(i,j) for j in j_range]
            j_range = j_range[::-1]
        loop += [(0, j) for j in range(n-1, -1, -1)]

    else:
        width = m // 2
        # right across top
        i_range = list(range(width))
        for j in range(1, n-1):
            loop += [(i,j) for i in i_range]
            i_range = i_range[::-1]
        loop += [(i, n-1) for i in range(m)]
        # left across bottom
        i_range = list(range(m-1, width-1, -1))
        for j in range(n-2, 0, -1):
            loop += [(i,j) for i in i_range]
            i_range = i_range[::-1]
        loop += [(i, 0) for i in range(m-1, -1, -1)]
    return loop
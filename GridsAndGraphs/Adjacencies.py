"""
Adjacency lists of the grid graph and some directed subgraphs.
"""

def find_Manhattan_distance_func(n):
    def ManhattanDistance(x, y):
        rx, cx = divmod(x, n)
        ry, cy = divmod(y, n)
        return abs(rx - ry) + abs(cx - cy)
    return ManhattanDistance

def find_grid_adjacency(m, n):
    """
    Returns adjacency list of mxn grid.
    Indexes cell (i,j) as i*n + j (row-major order),
    stores result as tuple of tuples.
    """
    UP, DOWN = -n, n
    LEFT, RIGHT = -1, 1

    adj = []
    row = 0
    col = 0
    index = 0
    for row in range(m):
        for col in range(n):
            # build neighbour list of node 'index'
            nb = []

            if row > 0:
                nb.append(index + UP)

            if row < m-1:
                nb.append(index + DOWN)

            if col > 0:
                nb.append(index + LEFT)

            if col < n-1:
                nb.append(index + RIGHT)

            adj.append(tuple(nb))
            index += 1

    # store structure as tuple of tuples
    return tuple(adj)


def find_reverse_adjacency(adjacency):
    rev_adj = [[] for _ in adjacency]
    for i, forward_edges in enumerate(adjacency):
        for j in forward_edges:
            rev_adj[j].append(i)
    return tuple(tuple(lst) for lst in rev_adj)


def find_grid_adjacency_dive(m, n):
    """
    The Diving subgraph
    """
    if m%2 == 0:
        adj = []
        i = 0   # row
        j = 0   # column
        for index in range(m*n):
            # build neighbour list of node 'index'
            nb = []

            # Left
            if (i == 0 and j>0) or (0 < i < m-1 and i%2==0 and 0 < j):
                nb.append(index - 1)

            # Right
            if (i == m-1 and j<n-1) or (0 < i < m-1 and i%2==1 and j < n-1):
                nb.append(index + 1)

            # Up
            if 0 < i and (j==n-1 or (0 < i < m-1 and i%2==0 and 0 < j < n-1)):
                nb.append(index - n)

            # Down
            if i < m-1 and (j==0 or (0 < i < m-1 and i%2==1 and 0 < j < n-1)):
                nb.append(index + n)
            
            adj.append(nb)

            # increment column, wrap row
            j += 1
            if j == n:
                j = 0
                i += 1

        # store structure as tuple of tuples
        return tuple(tuple(nb) for nb in adj)

    elif n%2 == 0:
        raise ValueError('Dive adjacency is not yet implemented for odd m, even n!')
    else:
        raise ValueError('Dive adjacency is not yet implemented for odd m*n!')

def find_grid_adjacency_dive_half(m, n):
    if m%2 == 0:
        adj = []
        i = 0   # row
        j = 0   # column
        for index in range(m*n):
            # build neighbour list of node 'index'
            nb = []

            # Left
            if (i == 0 and j>0) or (0 < i < m-1 and i%2==0 and 0 < j and j != n//2):
                nb.append(index - 1)

            # Right
            if (i == m-1 and j<n-1) or (0 < i < m-1 and i%2==1 and j < n-1 and j != n//2-1):
                nb.append(index + 1)

            # Up
            if 0 < i and (j==n-1 or (0 < i < m-1 and i%2==0 and j in (n//2-1, n//2))):
                nb.append(index - n)

            # Down
            if i < m-1 and (j==0 or (0 < i < m-1 and i%2==1 and j in (n//2-1, n//2))):
                nb.append(index + n)
            
            adj.append(nb)

            # increment column, wrap row
            j += 1
            if j == n:
                j = 0
                i += 1

        # store structure as tuple of tuples
        return tuple(tuple(nb) for nb in adj)

    elif n%2 == 0:
        raise ValueError('Dive adjacency is not yet implemented for odd m, even n!')
    else:
        raise ValueError('Dive adjacency is not yet implemented for odd m*n!')
    
def find_grid_adjacency_cell(m, n):
    """
    Returns adjacency list of mxn Cell grid.
    Indexes cell (i,j) as i*n + j (row-major order),
    stores result as tuple of tuples.
    """
    # even row = left, odd row = right
    # even col = down, odd col = up

    UP, DOWN = -n, n
    LEFT, RIGHT = -1, 1
    adj = []
    index = 0
    even_row = True
    for row in range(m):
        even_col = True
        for col in range(n):
            nb = []
            if even_col:
                if row < m-1:
                    nb.append(index+DOWN)
            elif row > 0:
                nb.append(index+UP)

            if even_row:
                if col > 0:
                    nb.append(index+LEFT)
            elif col < m-1:
                nb.append(index+RIGHT)

            adj.append(tuple(nb))
            index += 1
            even_col = not even_col
        even_row = not even_row

    # store structure as tuple of tuples
    return tuple(adj)
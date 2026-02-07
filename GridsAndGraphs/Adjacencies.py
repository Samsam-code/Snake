"""
The adjacency list of a directed graph is a list of 'out' edges of each vertex.
Here we define adjacency lists of the grid graph and some directed subgraphs,
stored these as tuples of tuples.
Row-major order is used: cell (i, j) is indexed as i * n + j.
"""

def find_reverse_adjacency(adjacency):
    """
    Returns the reverse adjacency list — the 'in' edges of each vertex.
    """
    rev_adj = [[] for _ in adjacency]
    for x, forward_edges in enumerate(adjacency):
        for y in forward_edges:
            rev_adj[y].append(x)
    return tuple(tuple(lst) for lst in rev_adj)

def find_adjacency_from_allowed_directions(allowed_directions):
    adjacency = []
    for vertex, dirs in enumerate(allowed_directions):
        adjacency.append(tuple([vertex+dir for dir in dirs]))
    return tuple(adjacency)

# now define each graph in terms of the allowed directions of each vertex


# ==== The grid ====

# Left      except first column
# Right     except last column
# Up        except first row
# Down      Except last row

def find_allowed_directions_grid(m, n):
    LEFT, RIGHT, UP, DOWN = -1, 1, -n, n
    allowed_directions = []
    for row in range(m):
        for column in range(n):
            dirs = []
            if column > 0:
                dirs.append(LEFT)
            if column < n-1:
                dirs.append(RIGHT)
            if row > 0:
                dirs.append(UP)
            if row < m-1:
                dirs.append(DOWN)
            allowed_directions.append(dirs)
    return allowed_directions

def find_adjacency_grid(m, n):
    return find_adjacency_from_allowed_directions(find_allowed_directions_grid(m, n))


# ==== The Dive directed subgraph ====

# Left      even rows except first column
# Right     odd rows except last column
# Up        last column except first row, even rows except first row / first column
# Down      first column except last row, odd rows except last row / last column 

# for odd m, even n, these could be flipped
# for odd m, odd n, a gadget could be attached to make this Theta-friendly

def find_allowed_directions_dive(m, n):
    if m%2:
        raise ValueError("Dive graph is defined only for even m!")
    LEFT, RIGHT, UP, DOWN = -1, 1, -n, n
    allowed_directions = []
    even_row = True
    for row in range(m):
        for column in range(n):
            dirs = []
            if even_row and 0 < column:
                dirs.append(LEFT)
            if not even_row and column < n-1:
                dirs.append(RIGHT)
            if 0 < row and ( column == n-1 or (even_row and 0 < column) ):
                dirs.append(UP)
            if row < m-1 and ( column == 0 or (not even_row and column < n-1) ):
                dirs.append(DOWN)
            allowed_directions.append(dirs)
        even_row = not even_row
    return allowed_directions        

def find_adjacency_dive(m, n):
    return find_adjacency_from_allowed_directions(find_allowed_directions_dive(m, n))
    

# ==== The Alternating-One-Way (AOW) directed subgraph ==== 

# Left      odd rows except first column
# Right     even rows except last column
# Up        odd columns except first row 
# Down      even columns except last row

# if m xor n is odd, a gadget could be attached to ensure a Hamiltonian Cycle exists
# for odd m, odd n, a gadget could be attached to make this Theta-friendly

def find_allowed_directions_AOW(m, n):
    if m%2 or n%2:
        raise ValueError("AOW graph is defined only for even side lengths!")
    LEFT, RIGHT, UP, DOWN = -1, 1, -n, n
    allowed_directions = []
    even_row = True
    even_col = True
    for row in range(m):
        for column in range(n):
            dirs = []
            if even_row and column > 0:
                dirs.append(LEFT)
            if not even_row and column < n-1:
                dirs.append(RIGHT)
            if not even_col and row > 0:
                dirs.append(UP)
            if even_col and row < m-1:
                dirs.append(DOWN)
            allowed_directions.append(dirs)
            even_col = not even_col
        even_row = not even_row
    return allowed_directions

def find_adjacency_AOW(m, n):
    return find_adjacency_from_allowed_directions(find_allowed_directions_AOW(m, n))
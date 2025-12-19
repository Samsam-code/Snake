"""
Some functions specialised to grid graphs.
"""

def find_grid_adjacency(m, n):
    """
    Returns adjacency list of mxn grid.
    Indexes cell (i,j) as i*n + j (row-major order),
    stores result as tuple of tuples.
    """
    adj = []
    i = 0   # row
    j = 0   # column
    for index in range(m*n):
        # build neighbour list of node 'index'
        nb = []

        # Left, except first column
        if j > 0:
            nb.append(index - 1)

        # Right, except last column
        if j < n-1:
            nb.append(index + 1)

        # Up, except first row
        if i > 0:
            nb.append(index - n)

        # Down, except last row
        if i < m-1:
            nb.append(index + n)
        
        adj.append(nb)

        # increment column, wrap row
        j += 1
        if j == n:
            j = 0
            i += 1

    # store structure as tuple of tuples
    return tuple(tuple(nb) for nb in adj)



def find_symmetry_transforms(m, n):
    # symmetries of rectangle
    # 0° rotation, horizontal flip, vertical flip, 180° rotation
    transforms = [
        lambda i, j: (i, j),
        lambda i, j: (m-1-i, j),
        lambda i, j: (i, n-1-j),
        lambda i, j: (m-1-i, n-1-j)
    ]

    if m == n:
        # bonus symmetries of square
        # main-diagonal flip, 90° rotation, 270° rotation, anti-diagonal flip
        transforms.extend([
            lambda i, j: (j, i),
            lambda i, j: (j, m-1-i),
            lambda i, j: (m-1-j, i),
            lambda i, j: (m-1-j, n-1-i)
        ])

    return transforms

def find_transformed_lists(m, n):
    transforms = find_symmetry_transforms(m, n)

    transformed_lists = []
    for func in transforms:
        func_list = [None] * (m*n)
        i = 0   # row
        j = 0   # column
        for index in range(m*n):
            ti, tj = func(i,j)
            func_list[index] = ti * n + tj
            j += 1
            if j == n:
                j = 0
                i += 1
        transformed_lists.append(func_list)
    return transformed_lists


def find_preferred_lists(transformed_lists):    
    return [
        [i<=v for i,v in enumerate(lst)]
        for lst in transformed_lists
    ]

def find_fixed_lists(transformed_lists):    
    return [
        [i==v for i,v in enumerate(lst)]
        for lst in transformed_lists
    ]

from fractions import Fraction
def find_geometric_lower_bound(m, n):
    # for each coordinate, find distance to the centre
    cm, cn = m//2, n//2
    m_distances = [abs(i-cm) for i in range(m)]
    n_distances = [abs(j-cn) for j in range(n)]
    distances = sorted([di+dj for di in m_distances for dj in n_distances])
    total = sum(distances)
    score_per_apple = []
    for empty_space in range(m*n-1, 0, -1):
        score_per_apple.append(Fraction(total, empty_space))
        total -= distances.pop()
    return score_per_apple
"""
Some simple Hamiltonian Cycles of even grids
and spanning Theta(m*n-3, 2, 2) subgraphs of odd grids.
"""


# ======== Hamiltonian Cycles ========


# ==== Some Tools ====

def find_HC_from_coords(HC_in_coords, n):
    return [i*n+j for i, j in HC_in_coords]

def find_indices_HC(loop):
    loop_indices = [None] * len(loop)
    for index, point in enumerate(loop):
        loop_indices[point] = index
    return loop_indices

def find_adjacent_indices_HC(adjacency, loop, loop_indices):
	adj_loop_indices = []
	for point in loop:
		temp = []
		for other_point in adjacency[point]:
			temp.append(loop_indices[other_point])
		adj_loop_indices.append(temp) 
	return adj_loop_indices

def find_list_loop_from_carved_loop(carved_loop, head=0):
    list_loop = []
    vertex = carved_loop[head]
    while vertex != head:
        list_loop.append(vertex)
        vertex = carved_loop[vertex]
    list_loop.append(head)
    return list_loop


# ==== The Haircomb HC ====

def find_HC_in_coords_haircomb(m, n):
    if m%2 == 0:    
        i_range = list(range(m))
        path = [(i,0) for i in i_range]
        j_range = list(range(1, n))
        for i in reversed(i_range):
            path += [(i, j) for j in j_range]
            j_range = j_range[::-1]
        return path
    elif n%2 == 0:
        j_range = list(range(n))
        path = [(0,j) for j in j_range]
        i_range = list(range(1, m))
        for j in reversed(j_range):
            path += [(i, j) for i in i_range]
            i_range = i_range[::-1]
        return path
    else:
        raise ValueError("HC undefined both side lengths are odd!")
    
def find_HC_haircomb(m, n):
    return find_HC_from_coords(find_HC_in_coords_haircomb(m, n), n)


# ==== The Coil HC ====

def find_HC_in_coords_coil(m, n):
    if m % 2 == 0:
        width = n // 2
        # down left side
        j_range = list(range(width))
        loop = []
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
        return loop

    elif n%2==0:
        width = m // 2
        # right across top
        i_range = list(range(width))
        loop = []
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
    else:
        raise ValueError("HC undefined both side lengths are odd!")
    
def find_HC_coil(m, n):
    return find_HC_from_coords(find_HC_in_coords_coil(m, n), n)


# ==== The Fractal Moore's Curve HC ===

def find_hilbert_curve(p):
    curve = [(0, 0)]
    n = 1
    for _ in range(p):
        q0 = [(y, x) for (x, y) in curve]
        q1 = [(x, y + n) for (x, y) in curve]
        q2 = [(x + n, y + n) for (x, y) in curve]
        q3 = [(2*n - 1 - y, n - 1 - x) for (x, y) in curve]
        curve = q0 + q1 + q2 + q3
        n *= 2
        print(curve)
    return curve

def find_HC_in_coords_Moore(m, n, fallback_HC=find_HC_haircomb):
    if not m==n:
        return fallback_HC(m, n)
    p = 0
    q = n
    while q > 1:
        q, r = divmod(q, 2)
        if r == 1:
            return fallback_HC(m, n)
        p += 1
    if p == 1:
        return [(0,0), (1,0), (1,1), (0,1)]
    half_size = n // 2
    H = reversed(find_hilbert_curve(p-1))
    A = [(half_size-1-x, half_size-1-y) for (x,y) in H]                       
    B = [(n-1-x, half_size-1-y) for (x,y) in H]                     
    C = [(x + half_size, y+half_size) for (x,y) in H]            
    D = [(x, y+half_size) for (x,y) in H] 
    return A+B+C+D

def find_HC_Moore(m, n):
    return find_HC_from_coords(find_HC_in_coords_Moore(m, n), n)



# ======== Theta Subgraphs ========


# ==== Some Tools ====

def find_theta_from_coords(theta_in_coords, n):
    long_path, (h1i, h1j), (h2i, h2j) = theta_in_coords
    long_path = [i*n+j for i,j in long_path]
    hole1 = h1i * n + h1j
    hole2 = h2i * n + h2j
    return long_path, hole1, hole2

# bad naming: this list is not a loop, but it makes Loop look clean in the Theta case
def find_loop_from_theta(theta):
    long_path, hole1, hole2 = theta
    return long_path + [hole1, hole2]

def find_indices_theta(theta):
    loop = find_loop_from_theta(theta)
    loop_indices = [None] * len(loop)
    for index, point in enumerate(loop):
        loop_indices[point] = index
    return loop_indices



# ==== The Haircomb Theta Subgraph ====

def find_theta_in_coords_haircomb(m, n):
    if (m*n)%2==0:
        raise ValueError("Theta undefined both side lengths are even!")
    hole1 = (0,0)
    hole2 = (1,1)
    long_path = [(i,0) for i in range(1, m)]
    j_range = list(range(1, n))
    for i in range(m-1, 1, -1):
        long_path += [(i,j) for j in j_range]
        j_range = j_range[::-1]
    for j in range(n-1, 0, -2):
        long_path += [(1, j), (0,j), (0, j-1), (1, j-1)]
    long_path.pop()
    return long_path, hole1, hole2

def find_theta_haircomb(m, n):
    return find_theta_from_coords(find_theta_in_coords_haircomb(m, n), n)
"""
Some simple Hamiltonian Cycles of even grids
and spanning Theta(m*n-3, 2, 2) subgraphs of odd grids.
"""

def find_loop_indices_HC(loop):
    loop_indices = [None] * len(loop)
    for index, point in enumerate(loop):
        loop_indices[point] = index
    return loop_indices

def find_loop_indices_Theta(loop, hole, antihole):
    loop_indices = [None] * (len(loop)+1)
    for index, point in enumerate(loop):
        loop_indices[point] = index
    loop_indices[hole] = loop_indices[antihole]
    return loop_indices


def find_adjacent_loop_indices(adjacency, loop, loop_indices):
	adj_loop_indices = []
	for point in loop:
		temp = []
		for other_point in adjacency[point]:
			temp.append(loop_indices[other_point])
		adj_loop_indices.append(temp) 
	return adj_loop_indices

def find_HC_haircomb(m, n):
    return [i*n+j for i, j in find_HC_haircomb_in_coords(m, n)]

def find_HC_haircomb_in_coords(m, n):
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
    
def find_theta_haircomb(m, n):
    path, (hi, hj), (ahi, ahj) = find_theta_haircomb_in_coords(m, n)
    path = [i*n+j for i,j in path]
    hole = hi * n + hj
    antihole = ahi * n + ahj
    return path, hole, antihole

def find_theta_haircomb_in_coords(m, n):
    if (m*n)%2==0:
        raise ValueError("Theta undefined both side lengths are even!")
    hole = (0,0)
    antihole = (1,1)
    loop = [(i,0) for i in range(1, m)]
    j_range = list(range(1, n))
    for i in range(m-1, 1, -1):
        loop += [(i,j) for j in j_range]
        j_range = j_range[::-1]
    for j in range(n-1, 0, -2):
        loop += [(1, j), (0,j), (0, j-1), (1, j-1)]
    return loop, hole, antihole

def find_HC_coil(m, n):
    return [i*n+j for i, j in find_HC_coil_in_coords(m, n)]

def find_HC_coil_in_coords(m, n):
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

def find_hilbert_curve(p):
    curve = [(0, 0)]
    n = 0
    for level in range(p):
        q0 = [(y, x) for (x, y) in curve]
        q1 = [(x, y + n) for (x, y) in curve]
        q2 = [(x + n, y + n) for (x, y) in curve]
        q3 = [(2*n - 1 - y, n - 1 - x) for (x, y) in curve]
        curve = q0 + q1 + q2 + q3
        n *= 2
    return curve

def find_HC_Moore(m, n, fallback_HC=find_HC_haircomb):
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
    H = find_hilbert_curve(p-1)
    A = [(n-1-x, n-1-y) for (x,y) in reversed(H)]                       
    B = [(2*n-1-x, n-1-y) for (x,y) in reversed(H)]                     
    C = [(x + n, y+n) for (x,y) in reversed(H)]            
    D = [(x, y+n) for (x,y) in reversed(H)] 
    return [x*n + y for (x,y) in A+B+C+D]

def find_HC_space_filling_H(m, n, fallback_HC=find_HC_haircomb):
    if not m==n:
        return fallback_HC(m, n)
    p = 0
    q = n
    while q > 1:
        q, r = divmod(q, 2)
        if r == 1:
            return fallback_HC(m, n)
        p += 1
    cell_to_move = ['Right', 'Down', 'Up', 'Left']
    length = 2
    for _ in range(p-1):
        new_length = length * 2

        # create four copies of previous in a 2x2 square
        new_cell_to_move = []
        for i in range(2):
            start = 0
            for row in range(length):
                for j in range(2):
                    for step in cell_to_move[start:start+length]:
                        new_cell_to_move.append(step)
                start += length
          
        
        # surgery the four copies together
        a = (length-1) * new_length + length-1
        b = a + 2
        c = a + new_length + 1
        d = a + new_length - 1
        new_cell_to_move[a] = 'Right'
        new_cell_to_move[b] = 'Down'
        new_cell_to_move[c] = 'Left'
        new_cell_to_move[d] = 'Up'
        
        cell_to_move = new_cell_to_move
        length = new_length

    update_location = {
        'Right':1,
        'Left' :-1,
        'Up'   :-length,
        'Down' :length
    }
    location = 0
    loop = []
    for _ in range(m*n):
        loop.append(location)
        location += update_location[cell_to_move[location]]
    return loop
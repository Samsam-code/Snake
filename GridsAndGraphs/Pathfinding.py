import heapq

INF = float("inf")

def find_Manhattan_distance_func(n):
    def Manhattan_distance(x, y):
        rx, cx = divmod(x, n)
        ry, cy = divmod(y, n)
        return abs(rx - ry) + abs(cx - cy)
    return Manhattan_distance

def find_Manhattan_heuristic1(n, target):
    ti, tj = divmod(target, n)
    def Manhattan_heuristic(x):
        xi, xj = divmod(x, n)
        return abs(ti-xi)+abs(tj-xj)
    return Manhattan_heuristic

def find_Manhattan_heuristic2(n):
    def find_Manhattan_heuristic1(target):
        ti, tj = divmod(target, n)
        def Manhattan_heuristic(x):
            xi, xj = divmod(x, n)
            return abs(ti-xi)+abs(tj-xj)
        return Manhattan_heuristic
    return find_Manhattan_heuristic1


def find_perimeter(m, n):
    vertex = 0
    perimeter = set([vertex])
    for _ in range(m-1):
        vertex += 1
        perimeter.add(vertex)
    for _ in range(n-1):
        vertex += n
        perimeter.add(vertex)
    for _ in range(m-1):
        vertex -= 1
        perimeter.add(vertex)
    for _ in range(n-1):
        vertex -= n
        perimeter.add(vertex)
    return perimeter


# ======== Standard Path Finding ========

# do not take into account that the snake can move out of the way


def astar(start, goal, blocked, adjacency, heuristic, limit=INF):
    """
    A* pathfinding from ``start`` to ``goal`` on a graph
    defined by ``adjacency`` with obstacles.
    """

    # Priority queue: (heuristic, -score, cell)
    prio_queue = []
    heapq.heappush(prio_queue, (heuristic(start, goal), 0, start))
    
    came_from = {}
    score = {start: 0}
    
    while prio_queue:
        _, negative_score, current = heapq.heappop(prio_queue)
        
        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        
        new_score = 1 - negative_score
        for neighbor in adjacency[current]:
            if neighbor in blocked or new_score >= score.get(neighbor, limit+1):
                continue
            
            score[neighbor] = new_score
            h_score = new_score + heuristic(neighbor, goal)
            if h_score <= limit:
                came_from[neighbor] = current
                heapq.heappush(prio_queue, (h_score, -new_score, neighbor))
    return None



# ======== Safe Path Finding ========

# take into account the snake will move, so spaces become unblocked over time
# on a safe graph, such as the AOW or Dive subgraphs, this will always give a path


def find_barrier_costs_from_carved_path(tail, head, carved_path):
    barrier_costs = [0] * len(carved_path)
    counter = 1
    vertex = tail
    barrier_costs[vertex] = counter
    while vertex != head:
        counter += 1
        vertex = carved_path[vertex]
        barrier_costs[vertex] = counter    
    return barrier_costs
    
def safe_path_finder_BFS(start, end, barrier_costs, adjacency):
    barrier_costs[start] = INF   # hack: prevents failure in back-tracking via parent_of
    
    area = len(adjacency)
    parent_of = [None] * area
    stack = [start]
    next_stack = []
    distance = 1
    while stack:
        
        while stack:
            vertex = stack.pop()            
            for neighbour in adjacency[vertex]:
                if parent_of[neighbour] != None:
                    continue
                if distance < barrier_costs[neighbour]:
                    continue

                if neighbour == end:
                    path = [end]
                    while vertex != start:
                        path.append(vertex)
                        vertex = parent_of[vertex]
                    return path[::-1]

                parent_of[neighbour] = vertex
                next_stack.append(neighbour)
        
        stack, next_stack = next_stack, []
        distance += 1
    return None

# an A* implemetation should be faster


# ======== Expensive Safe Path Finding ========

# safe as above, but finds the optimal path
# checks every possible path, so is VERY SLOW!!


def astar_with_temporary_obstacles(start, goal, blocked, adjacency, heuristic, limit=INF):
    # blocked is a dict {cell: end_time}
    # cells are blocked from t=0 until their end_time.
    
    # Priority queue: (heuristic, -score, cell, path)
    prio_queue = []
    heapq.heappush(prio_queue, (heuristic(start, goal), 0, start, [start]))
    
    visited = set()
    visited.add((start, 0))
    
    while prio_queue:
        _, negative_score, current, path = heapq.heappop(prio_queue)
        
        if current == goal:
            return path[1:]
        
        new_score = 1 - negative_score
        for neighbor in adjacency[current]:
            
            # Obstacle check
            if new_score <= blocked.get(neighbor, 0):
                continue
            
            # No revisiting cells
            if neighbor in path:
                continue
            
            state = (current, new_score)
            if state not in visited:
                visited.add(state)
                h_score = new_score + heuristic(neighbor, goal)
                if h_score<=limit:
                    heapq.heappush(prio_queue, (h_score, -new_score, neighbor, path + [neighbor]))

    return None

# You could be smart, and use a cheap one first, and then use the expensive one, throwing out paths longer than the cheap path...



# ======== Transition to Hamiltonian Cycle ========

# on a safe graph, such as the AOW or Dive subgraphs,
# it is possible to re-orient the snake to lie along a Hamiltonian Cycle in O(A) time


def inflate_by_walking_away(start, end, adjacency, carved_path, visited_vertices, distance_to_target):
    # go for a walk between the start and end,
    # choosing at each step the furthest unvisited vertex from the end
    vertex = start
    visited_vertices.remove(end)    # hack: will be re-added by the following code
    while vertex != end:
        best_dist = -INF
        next_vertex = None
        for neighbour in adjacency[vertex]:
            if neighbour in visited_vertices:
                continue
            dist = distance_to_target(neighbour)
            if dist > best_dist:
                best_dist = dist
                next_vertex = neighbour
        visited_vertices.add(next_vertex)
        carved_path[vertex] = next_vertex
        vertex = next_vertex
    return

def inflate_by_walking_blindly(start, end, adjacency, carved_path, visited_vertices):
    # DOES NOT WORK YET!
    # go for a walk between the start and end, 
    # avoiding the end if possible
    # can be used without a distance heuristic but will take a little longer
    vertex = start
    visited_vertices.remove(end)    # hack: will be re-added by the following code
    while vertex != end:
        for neighbour in adjacency[vertex]:
            if neighbour in visited_vertices:
                continue
            next_vertex = neighbour
            break
        else:
            next_vertex = end
        visited_vertices.add(next_vertex)
        carved_path[vertex] = next_vertex
        vertex = next_vertex
    return

def transition_to_HC(solver):
    carved_path = solver.carved_path
    adjacency = solver.adjacency

    tail = solver.tail
    head = solver.head
    apple = solver.apple
    
    # track what vertices are in the loop, starting with those in the snake
    vertex = tail
    visited_vertices = set([tail])
    while vertex != head:
        vertex = carved_path[vertex]
        visited_vertices.add(vertex)

    # define how to inflate the loop  between the start and end
    # recommended to use a distance heursitic, but not important
    if hasattr(solver, "find_distance_heuristic_func"):
        def inflate_between(start, end):
            distance_heuristic = solver.find_distance_heuristic_func(end)
            return inflate_by_walking_away(start, end, adjacency, carved_path, visited_vertices, distance_heuristic)
    else:
        def inflate_between(start, end):
            return inflate_by_walking_blindly(start, end, adjacency, carved_path, visited_vertices)

    # connect head to tail to form a loop
    if tail in adjacency[head]:
        carved_path[head] = tail
    else:
        inflate_between(head, tail)

    # inflate the loop until it fills the space - becomes a Hamiltonian Cycle
    next_vertex = carved_path[head]
    while len(visited_vertices) != len(adjacency):
        for neighbour in adjacency[head]:
            if neighbour in visited_vertices: 
                continue
            inflate_between(head, next_vertex)
            next_vertex = carved_path[head]
            break
        
        head = next_vertex
        next_vertex = carved_path[head]
        if head == apple:
            yield apple
            apple = solver.apple
            continue
        yield head
        tail = carved_path[tail]
    
    # wonderful, now carved_path is a loop! to read it, use find_loop_list_from_carved_path
    solver.tail = tail
    solver.head = head
    return
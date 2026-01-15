import heapq

INF = float("inf")

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
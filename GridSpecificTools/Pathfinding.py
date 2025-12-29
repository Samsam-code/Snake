import heapq

INF = float("inf")

def astar(start, goal, blocked, adjacency, heuristic, limit=INF):
    """
    A* pathfinding from ``start`` to ``goal`` on a graph
    defined by ``adjacency`` with obstacles.
    """
    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), 0, start))
    
    came_from = {}
    g_score = {start: 0}
    
    while open_set:
        _, current_g, current = heapq.heappop(open_set)
        
        if current == goal:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        
        for neighbor in adjacency[current]:
            # Check bounds and obstacles
            tentative_g = current_g + 1
            if neighbor not in blocked and tentative_g < g_score.get(neighbor, limit+1):
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                if f_score <= limit:
                    came_from[neighbor] = current
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor))
    return None
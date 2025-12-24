from GridSpecificTools.GridGraphAndSymmetries import find_grid_adjacency, find_Manhattan_distance_func
import heapq

def astar(start, goal, blocked, adjacency, heuristic):
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
            path.append(start)
            return path[::-1]
        
        for neighbor in adjacency[current]:
            # Check bounds and obstacles
            if (neighbor not in blocked):
                tentative_g = current_g + 1
                
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor))
    
    return None  # No path found

class Optimizer_FastForward:
    def __init__(self, SolverClass, m, n, *args, **kwargs):
        self.solver = SolverClass(m, n, *args, **kwargs)
        self.name = self.solver.name + " + FF"

        # Avoid doing adjacency computation twice if possible
        self.adjacency = self.solver.adjacency if hasattr(self.solver, "adjacency") else find_grid_adjacency(m, n)
        self.ManhattanDistance = find_Manhattan_distance_func(n)
        
    def find_path(self, apple):
        snake = self.solver.snake[:]
        l = self.solver.snake_length
        head = snake[-1]

        basic_path = self.solver.find_path(apple)
        if len(basic_path)<= l:
            return basic_path
        
        end_path = basic_path[len(basic_path)-l+1:]

        target = basic_path[-l]
        blocked = set(snake).union(end_path)
        head_to_target = astar(head, target, blocked, self.adjacency, self.ManhattanDistance)

        if head_to_target is None:
            return basic_path
        else:
            return head_to_target[1:]+end_path
    
    # If we want to get any other attribute than those we have defined,
    # go search them in the solver
    def __getattr__(self, name): 
        return getattr(self.solver, name)



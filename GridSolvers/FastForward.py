from GridsAndGraphs.Adjacencies import find_grid_adjacency, find_Manhattan_distance_func
from GridsAndGraphs.Pathfinding import astar

class Optimizer_FastForward:
    def __init__(self, SolverClass, m, n, *args, end_FF=None, **kwargs):
        self.solver = SolverClass(m, n, *args, **kwargs)
        self.name = self.solver.name + " + FF"

        # Avoid doing adjacency computation twice if possible
        self.adjacency = self.solver.adjacency if hasattr(self.solver, "adjacency") else find_grid_adjacency(m, n)
        self.ManhattanDistance = find_Manhattan_distance_func(n)

        self.end_FF = end_FF or m*n//2

    def start_new_game(self, start):
        self.solver.start_new_game(start)
        self.find_path = self.find_path_FF
        
    def find_path_FF(self, apple):
        l = self.solver.snake_length
        if self.end_FF<= l:
            self.find_path = self.solver.find_path
            return self.solver.find_path(apple)
        
        snake = self.solver.snake.copy()
        head = snake[-1]

        basic_path = list(self.solver.find_path(apple))
        if len(basic_path)<= l:
            return basic_path
        
        end_path = basic_path[len(basic_path)-l+1:]

        target = basic_path[-l]
        blocked = set(snake).union(end_path)
        head_to_target = astar(head, target, blocked, self.adjacency, self.ManhattanDistance, len(basic_path)-l)

        if head_to_target is None:
            return basic_path
        else:
            return head_to_target+end_path
    
    # If we want to get any other attribute than those we have defined,
    # go search them in the solver
    def __getattr__(self, name): 
        return getattr(self.solver, name)



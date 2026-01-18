from GridsAndGraphs.Adjacencies import find_grid_adjacency_cell, find_Manhattan_distance_func
from GridsAndGraphs.Pathfinding import astar_temp_obstacles

class GridSolver_SafeAstar:

    def __init__(self, m, n):
        self.name = "Safe A*"
        self.area = m*n
        self.adjacency = find_grid_adjacency_cell(m, n)
        self.ManhattanDistance = find_Manhattan_distance_func(n)

    def start_new_game(self, start):
        self.snake = [start]
        self.snake_length = 1

    def find_path(self, apple):
        l = self.snake_length
        snake = self.snake
        head = snake[-1]

        blocked = {snake[i]:i for i in range(l)}
        path = astar_temp_obstacles(head, apple, blocked, self.adjacency, self.ManhattanDistance, self.area)

        self.update_snake(path)
        
        return path
    
    def update_snake(self, path):
        self.snake_length += 1

        p = len(path)
        if self.snake_length <= p:
            # Tail is entirely in path
            self.snake = path[-self.snake_length:]
        else:
            # Tail includes all of path + last part of snake
            need_from_snake = self.snake_length - p
            self.snake = self.snake[-need_from_snake:] + path
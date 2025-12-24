from GridSpecificTools.GridGraphAndSymmetries import find_grid_adjacency, find_Manhattan_distance_func
from GridSpecificTools.CycleAndTheta import find_HC_haircomb, find_theta_haircomb
from collections import deque
from itertools import islice

class GridSolver_LoopAndGreedySkip():
    def __init__(self, m, n, find_HC=find_HC_haircomb, find_theta=find_theta_haircomb, cutoff_length=None):
        if m%2 == 0 or n%2 == 0:
            self.name = 'Loop&GreedySkip'
            self.start_new_game = self.start_new_game_even
            self.find_path = self.find_path_even
            loop = find_HC(m, n)
        else:
            raise ValueError('Loop&Skip not yet implemented for odd grids!')
            
        self.area = m * n
        self.adjacency = find_grid_adjacency(m, n)
        self.loop = deque(loop)
        self.loop_indices = [None] * self.area
        self.cutoff_length = cutoff_length if cutoff_length is not None else self.area // 2

        self.ManhattanDistance = find_Manhattan_distance_func(n)

    def start_new_game_even(self, start):
        self.snake_length = 1
        self.snake = [start]
        # rotate so head (start) is last in loop
        i = self.loop.index(start)+1
        self.loop.rotate(-i)
        self.update_loop_indices()

    def find_path_even(self, apple):
        # path from basic looping
        i = self.loop_indices[apple]+1
        path = list(islice(self.loop, i))

        # if the loop is an inefficient path to the apple, try skipping
        dist_to_apple = self.ManhattanDistance(self.snake[-1], apple)
        if len(path) > dist_to_apple and self.snake_length < self.cutoff_length:
            path = self.greedy_skip(path)

        # update internal state, then pass path to outside world
        self.update_snake(path)
        self.loop.rotate(-i)
        self.update_loop_indices()
        return path


    def update_loop_indices(self):
        for i, v in enumerate(self.loop):
            self.loop_indices[v] = i

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

    def greedy_skip(self, path):

        path.insert(0, self.snake[-1])
        result = []
        shortcut_amount = 0
        i = 0
        steps = 0
        while i < len(path) - 1:
            # The farthest we can look ahead is limited
            if steps<self.snake_length:
                limit = self.loop_indices[self.snake[steps]]-steps
                max_jump = min(len(path)-1, i + limit - shortcut_amount + 1)
            else:
                max_jump = len(path) - 1

            best_j = i
            best_adj = None
            for adj in self.adjacency[path[i]]:
                j = self.loop_indices[adj]+1
                if best_j < j <= max_jump:
                    best_j = j
                    best_adj = adj
                    if j == max_jump:
                        break
            result.append(best_adj)
            shortcut_amount += best_j - i - 1
            i = best_j
            steps += 1

        return result
    
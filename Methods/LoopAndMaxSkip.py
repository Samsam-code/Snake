from GridSpecificTools.GridGraphAndSymmetries import find_grid_adjacency, find_Manhattan_distance_func
from GridSpecificTools.CycleAndTheta import find_HC_haircomb, find_theta_haircomb
from collections import deque
from itertools import islice


class GridSolver_LoopAndMaxSkip():
    def __init__(self, m, n, find_HC=find_HC_haircomb, find_theta=find_theta_haircomb, cutoff_length=None):
        if m%2==0 or n%2==0:
            self.name = 'Loop&MaxSkip'
            self.start_new_game = self.start_new_game_even
            self.find_path = self.find_path_even
            loop = find_HC(m, n)
        else:
            print('Loop&Skip not yet implemented for odd grids!')

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
            path = self.greedy_skip(apple)

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

    def greedy_skip(self, apple):
        apple_idx = self.loop_indices[apple]

        tail_indices = []
        for x in self.snake:
            idx = self.loop_indices[x]
            if idx > apple_idx:
                break
            tail_indices.append(idx)
        
        # for each node, measure how many tail sections are not in front of it
        # make the cost for the apple one higher
        barrier = [0] * (apple_idx + 1)
        if tail_indices:
            for idx, t in enumerate(tail_indices):
                barrier[t] = idx+1
            barrier[-1] = idx + 2
        
        # flow backwards from apple
        # each node inherits best path to apple from its neighbours closer to apple
        children = [None] * (apple_idx + 1)
        apple_distance = [None] * (apple_idx + 1)
        apple_distance[apple_idx] = 0
        for idx in range(apple_idx-1, -1, -1):
            best = None
            child = None
            
            for x in self.adjacency[self.loop[idx]]:
                j = self.loop_indices[x] 

                # the neighbour must between you and the apple
                if not (idx < j <= apple_idx):
                    continue
                
                # can we possibly pay this barrier from this direction?
                # at most idx+1 moves to get to idx, another to get to j
                barrier_j = barrier[j]
                if idx + 2 < barrier_j:
                    continue

                lower_bound = apple_distance[j] + barrier_j
                if (best is None) or (lower_bound < best):
                    # is better than other paths
                    best = lower_bound
                    child = j
                
            # idx inherits from this child
            apple_distance[idx] = apple_distance[child] + 1 
            barrier[idx]        = max(barrier[idx], barrier[child] - 1)
            children[idx]       = child


        # find best first step on path from head to apple
        best_score = None
        for x in self.adjacency[self.snake[-1]]:
            j = self.loop_indices[x]
            if not (0 <= j <= apple_idx and barrier[j] <= 1):
                continue
            if best_score is None or apple_distance[j] < best_score:
                best_score = apple_distance[j]
                start_index = j
                path = [x]

        # trace path from there to apple
        idx = start_index
        while idx < apple_idx:
            idx = children[idx]
            path.append(self.loop[idx])

        return path
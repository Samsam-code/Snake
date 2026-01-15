"""
A grid solver which follows the 'Loop' strategy.
Sticks to a Hamiltonian Cycle, unless the grid has odd area A, 
then it follows a spanning Theta(A-3, 2, 2) subgraph.
"""
from GridsAndGraphs.CycleAndTheta import find_HC_haircomb, find_theta_haircomb, find_loop_indices_HC, find_loop_indices_Theta
from itertools import islice, chain


class GridSolver_Loop():
    def __init__(self, m, n, find_HC = find_HC_haircomb, find_theta = find_theta_haircomb):
        self.name = 'Loop'
        self.area = m*n
        is_even_grid = ((m*n)%2 == 0)

        if is_even_grid:
            self.start_new_game = self.start_new_game_even
            self.find_path = self.find_path_even
            self.loop = find_HC(m, n)
            self.estimate_moves_per_apple = self.estimate_moves_per_apple_even
            self.loop_indices = find_loop_indices_HC(self.loop)
        else:
            self.start_new_game = self.start_new_game_odd
            self.find_path = self.find_path_odd
            self.loop, self.hole, antihole = find_theta(m, n)
            self.loop_indices = find_loop_indices_Theta(self.loop, self.hole, antihole)
            self.loop_indices[self.hole] = self.loop_indices[antihole]

    def start_new_game_even(self, start):
        self.index_head = self.loop.index(start)
        self.snake_length = 1

    @property
    def snake(self):
        j = self.index_head+1
        i = j-self.snake_length
        if i>=0:
            return self.loop[i:j]
        l = len(self.loop)
        return self.loop[i+l:l]+self.loop[:j]

    def find_path_even(self, apple):
        loop = self.loop
        j = self.loop_indices[apple]
        i, self.index_head = self.index_head, j
        self.snake_length+=1
        if i < j:
            return islice(loop, i+1, j+1)
        return chain(
            islice(loop, i+1, len(loop)),
            islice(loop, 0, j+1)
        )
    
    def estimate_moves_per_apple_even(self):
        area = self.area
        return [(area - apples_eaten) / 2 for apples_eaten in range(area-1)]
    

    # the odd case is the same, but we keep track of the hole and antihole
    def start_new_game_odd(self, start):
        if start == self.hole:
            self.hole, self.loop[-1] = self.loop[-1], self.hole
        self.index_head = self.loop.index(start)
        self.snake_length = 1

    def find_path_odd(self, apple):
        loop = self.loop
        if apple == self.hole:
            self.hole, loop[-1] = loop[-1], self.hole
        j = self.loop_indices[apple]
        i, self.index_head = self.index_head, j
        self.snake_length += 1
        if i < j:
            return islice(loop, i+1, j+1)
        return chain(
            islice(loop, i+1, len(loop)),
            islice(loop, 0, j+1)
        )
"""
A grid solver which follows the 'Loop' strategy.
Sticks to a Hamiltonian Cycle, unless the grid has odd area A, 
then it follows a spanning Theta(A-3, 2, 2) subgraph.

Loop odd is very very broken...
"""
from collections import deque
from GridSpecificTools.CycleAndTheta import find_HC, find_theta
from itertools import islice


class GridSolverLoop():
    def __init__(self, m, n):
        if m%2==0 or n%2==0:
            self.name = 'Loop Even'
            self.start_new_game = self.start_new_game_even
            self.find_path = self.find_path_even
            self.loop = deque(find_HC(m, n))
            
        else:
            self.name = 'Loop Odd'
            self.start_new_game = self.start_new_game_odd
            self.find_path = self.find_path_odd
            
            loop, h, ah, ahi = find_theta(m, n)
            self.loop = deque(loop)
            self.hole = h
            self.antihole = ah
            self.antihole_idx = ahi
            self.area = m*n
            
        
    def start_new_game_even(self, start):
        # rotate so head (start) is last in loop
        i = self.loop.index(start)+1
        self.loop.rotate(-i)

    def find_path_even(self, apple):
        # rotate so next head (apple) is last in loop
        i = self.loop.index(apple)+1
        path = list(islice(self.loop, i))
        self.loop.rotate(-i)
        return path

    # the odd case is the same, but we keep track of the hole and antihole
    def start_new_game_odd(self, start):
        if start == self.hole:
            # swap hole and antihole, so start is in loop
            self.hole, self.antihole = self.antihole, self.hole
            self.loop[self.antihole_idx] = self.antihole
        # rotate so head (start) is last in loop
        i = self.loop.index(start)+1
        self.loop.rotate(-i)
        self.antihole_idx = (self.antihole_idx - i) % (self.area-1)

    def find_path_odd(self, apple):
        if apple == self.hole:
            print()
            # swap hole and antihole, so apple is in loop
            print(self.hole, self.antihole)
            self.hole, self.antihole = self.antihole, self.hole
            print(self.hole, self.antihole)
            self.loop[self.antihole_idx] = self.antihole
        # rotate so next head (apple) is last in loop
        i = self.loop.index(apple)+1
        path = list(islice(self.loop, i))
        self.loop.rotate(-i)
        self.antihole_idx = (self.antihole_idx - i) % (self.area-1)
        return path
"""
A grid solver which follows the 'Loop' strategy.
Sticks to a Hamiltonian Cycle, unless the grid has odd area A, 
then it follows a spanning Theta(A-3, 2, 2) subgraph.
"""
from GridsAndGraphs.CycleAndTheta import find_HC_haircomb, find_theta_haircomb

class GridSolver_Loop():
    def __init__(self, m, n, find_HC = find_HC_haircomb, find_theta = find_theta_haircomb):
        self.name = 'Loop'
        exists_HC = m%2==0 or n%2==0
        if exists_HC:
            self.loop = find_HC(m, n)
            self.yield_moves_to_simulator = self.yield_moves_to_simulator_HC
        else:
            self.theta = find_theta(m, n)
            self.yield_moves_to_simulator = self.yield_moves_to_simulator_theta

    def yield_moves_to_simulator_HC(self, start):
        loop = self.loop
        yield from loop[loop.index(start)+1:]
        while True:
            yield from loop

    def yield_moves_to_simulator_theta(self, start):
        long_path, hole1, hole2 = self.theta
        if start == hole1 or start == hole2:
            yield from long_path
        else:
            yield from long_path[long_path.index(start)+1:]
        while True:
            yield hole2 if self.apple == hole2 else hole1
            yield from long_path
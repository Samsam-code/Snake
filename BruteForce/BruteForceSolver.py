"""
Brute force calculate the EV by building the optimal-play graph.

MEMORY WARNING: The spacial complexity is exponential.
Start with small values!
"""
from BruteForce.TreeBasics import OptimalSnakeTree
from GridsAndGraphs.Adjacencies import find_adjacency_grid


class BruteForceSolver_Template(OptimalSnakeTree):
    def __init__(self, adjacency):
        super().__init__(adjacency)
        self.build_optimal_graph()
        self.name = 'BruteForce'

    def move_generator(self, start):
        current_node = self.root.children[start]
        while True:
            current_node = current_node.apple_to_move[self.apple]
            yield current_node.value
    
class GridSolver_BruteForce(BruteForceSolver_Template):
     def __init__(self, m, n, find_adjacency = find_adjacency_grid):
        super().__init__(find_adjacency(m, n))
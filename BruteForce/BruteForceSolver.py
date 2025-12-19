"""
Brute force calculate the EV by building the optimal-play graph.

MEMORY WARNING: The spacial complexity is exponential.
Start with small values!
"""
from BruteForce.TreeBasics import OptimalSnakeTree
from GridSpecificTools.GridGraphAndSymmetries import find_grid_adjacency

class GridSolverOptimal(OptimalSnakeTree):
    def __init__(self, m, n):
        super().__init__(find_grid_adjacency(m, n))
        self.build_optimal_graph()
        self.name = 'Arfen\'s Optimal'
    
    def start_new_game(self, start):
        self.current_node = self.root.children[start]

    def find_path(self, apple):
        # follow the move sequence until you hit the apple
        path = []
        temp_node = self.current_node
        while temp_node.value != apple:
            temp_node = temp_node.apple_to_move[apple]
            path.append(temp_node.value)
        self.current_node = temp_node
        return path
from GridSolvers.Templates import GridSolverTemplate_to_Loop
from GridsAndGraphs.Adjacencies import find_adjacency_AOW
from GridsAndGraphs.Pathfinding import safe_path_finder_BFS, find_barrier_costs_from_carved_path

class GridSolver_SPF_AOW_BFS(GridSolverTemplate_to_Loop):
    def __init__(self, m, n, name='SPF AOW BFS', cutoff='BEST GUESS'):
        if cutoff == 'BEST GUESS':
            const = 0.62    # looks good on the 32x32 grid
            cutoff = int( m * n * const)
        super().__init__(m, n, find_adjacency=find_adjacency_AOW, name=name, cutoff=cutoff)

    def find_moves(self):
        barrier_costs = find_barrier_costs_from_carved_path(self.tail, self.head, self.carved_path)
        return safe_path_finder_BFS(self.head, self.apple, barrier_costs, self.adjacency)
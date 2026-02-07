# ======== Graph Solver Template ========


# ==== Basic Template ====

# to use this, make a subclass with a method called self.find_moves
# alternatively, self.find_and_commit_moves can be overwritten — see Drone's Rules

class GraphSolverTemplate:
    def __init__(self, adjacency, name=''):
        self.adjacency = adjacency
        self.name = name
        self.area = len(adjacency)

    def yield_moves_to_simulator(self, start):
        self.carved_path = [None] * self.area
        self.head = start
        self.tail = start

        while True:
            yield from self.find_and_commit_moves()

    def find_and_commit_moves(self):
        # intermediate step to centralise responsibilty of tracking the snake via carved_path
        carved_path = self.carved_path
        tail = self.tail
        head = self.head
        apple = self.apple 
        for new_head in self.find_moves():  
            carved_path[head] = new_head 
            head = new_head
            if new_head == apple:
                self.tail = tail
                self.head = apple
                yield apple   
                return   
            new_tail = carved_path[tail]
            carved_path[tail] = None       
            tail = new_tail
            yield head


# ==== Transition to Loop ====

from GridsAndGraphs.Pathfinding import transition_to_HC
from GridsAndGraphs.CycleAndTheta import find_list_loop_from_carved_loop

class GraphSolverTemplate_to_Loop(GraphSolverTemplate):
    def __init__(self, adjacency, name='', cutoff=None):
        super().__init__(adjacency, name)
        self.cutoff = cutoff if cutoff is not None else len(adjacency)

    def yield_moves_to_simulator(self, start):
        self.carved_path = [None] * self.area
        self.loop = None
        self.head = start
        self.tail = start

        for apples_eaten in range(self.cutoff):
            yield from self.find_and_commit_moves()

        yield from transition_to_HC(self)

        loop = find_list_loop_from_carved_loop(self.carved_path)
        self.loop = loop
        yield from loop[loop.index(self.head)+1:]
        while True:
            yield from loop


# ==== Transition to DHCR ====

# coming soon ;)



# ======== Grid Solvers ========

# can quickly be built from the general graph template above
# only important difference is the Manhattan distance, and the side-lengths for row-major ordering or whatnot

from GridsAndGraphs.Pathfinding import find_Manhattan_heuristic2

def grid_solver_common_intialisation(self, m, n, adjacency=None, find_adjacency=None):
    self.m = m
    self.n = n
    self.find_distance_heuristic_func = find_Manhattan_heuristic2(n)
    if adjacency is None:
        if find_adjacency is None:
            raise ValueError('Must inlclude either adjacency or find_adjacency')
        else:
            return find_adjacency(m, n)
    else:
        return adjacency
    
class GridSolverTemplate(GraphSolverTemplate):
    def __init__(self, m, n, adjacency=None, find_adjacency=None,  name='',):
        adjacency = grid_solver_common_intialisation(self, m, n, adjacency=adjacency, find_adjacency=find_adjacency)
        super().__init__(adjacency, name=name)

class GridSolverTemplate_to_Loop(GraphSolverTemplate_to_Loop):
    def __init__(self, m, n, adjacency=None, find_adjacency=None,  name='', cutoff=None):
        adjacency = grid_solver_common_intialisation(self, m, n, adjacency=adjacency, find_adjacency=find_adjacency)
        super().__init__(adjacency, name=name, cutoff=cutoff)
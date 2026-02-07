from GridsAndGraphs.Adjacencies import find_adjacency_grid
from GridsAndGraphs.CycleAndTheta import find_HC_haircomb, find_indices_HC, find_adjacent_indices_HC

def greedy_skip(solver): 
    neighbouring_loop_indices = solver.neighbouring_loop_indices
    carved_path_index = solver.carved_path_index
    loop = solver.loop
    area = solver.area

    index_tail = solver.index_tail
    index_head = solver.index_head
    index_apple = solver.loop_indices[solver.apple]

    while True:

        if index_head < index_apple:
            best_new_index = index_head
            for possible_new_index in neighbouring_loop_indices[index_head]:
                if possible_new_index < best_new_index:
                    continue
                if index_apple < possible_new_index:
                    continue
                if index_head < index_tail < possible_new_index:
                    continue 
                best_new_index = possible_new_index

        elif index_head < index_tail:
            best_new_index = index_head
            for possible_new_index in neighbouring_loop_indices[index_head]:
                if possible_new_index < best_new_index:
                    continue
                if index_tail < possible_new_index:
                    continue
                best_new_index = possible_new_index

        else:
            best_score = index_head - area
            first_obstacle = min(index_tail, index_apple)
            for possible_new_index in neighbouring_loop_indices[index_head]:
                if index_head < possible_new_index:
                    score = possible_new_index - area
                elif first_obstacle < possible_new_index:
                    continue
                else:
                    score = possible_new_index
            
                if score <= best_score:
                    continue
                best_new_index = possible_new_index

        # commit this move
        carved_path_index[index_head] = best_new_index 
        if best_new_index == index_apple:
            solver.index_head = index_apple
            solver.index_tail = index_tail
            yield loop[index_apple]
            return
        index_head = best_new_index 
        index_tail = carved_path_index[index_tail]
        yield loop[best_new_index]
    # since only certain transitions are allowed between the states
    # this implementation *could* be slightly optimised



class GridSolver_LoopAndSkip:
    def __init__(self, m, n, find_HC=find_HC_haircomb, cutoff_length=None, loop_and_skip=greedy_skip):
        self.name = 'Loop&Skip'
        self.area = m * n
        self.adjacency = find_adjacency_grid(m, n)
        self.cutoff_length = cutoff_length if cutoff_length is not None else self.area // 2
        self.carved_path_index = [None] * self.area

        exists_HC = m%2==0 or n%2==0
        if exists_HC:
            self.loop = find_HC(m, n)
            self.loop_indices = find_indices_HC(self.loop)
            self.neighbouring_loop_indices = find_adjacent_indices_HC(self.adjacency, self.loop, self.loop_indices)
            self.yield_moves_to_simulator = self.yield_moves_to_simulator_HC
            self.estimate_moves_per_apple = self.estimate_moves_per_apple_HC
            self.loop_and_skip = loop_and_skip
        else:
            raise ValueError('Solver not implemented on odd-by-odd grids!')
            
    def yield_moves_to_simulator_HC(self, start):
        index_start = self.loop_indices[start]
        self.index_head = index_start
        self.index_tail = index_start

        for apples_eaten in range(self.cutoff_length):
            yield from self.loop_and_skip(self)

        loop = self.loop
        yield from loop[self.index_head+1:]
        while True:
            yield from loop

 
    def estimate_moves_per_apple_HC(self):
        area = self.area
        pre_cutoff = [(apples_eaten) / 2 for apples_eaten in range(self.cutoff_length)]
        post_cutoff = [(area - apples_eaten) / 2 for apples_eaten in range(self.cutoff_length, area-1)]
        return pre_cutoff + post_cutoff
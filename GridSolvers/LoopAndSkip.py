from GridsAndGraphs.Adjacencies import find_grid_adjacency
from GridsAndGraphs.CycleAndTheta import find_HC_haircomb, find_theta_haircomb, find_loop_indices_HC, find_adjacent_loop_indices
from itertools import islice, chain

class GridSolver_LoopAndGreedySkip():
    def __init__(self, m, n, find_HC=find_HC_haircomb, find_theta=find_theta_haircomb, cutoff_length=None):
        self.name = 'Loop&GreedySkip'
        self.area = m * n
        self.adjacency = find_grid_adjacency(m, n)
        self.cutoff_length = cutoff_length if cutoff_length is not None else self.area // 2
        self.where_index_head_went = [None] * self.area

        is_even_grid = ((m*n)%2 == 0)
        if is_even_grid:
            self.start_new_game = self.start_new_game_even
            self.find_path = self.find_path_even
            self.loop = find_HC(m, n)
            self.estimate_moves_per_apple = self.estimate_moves_per_apple_even
        else:
            raise ValueError('Solver not implemented on odd-by-odd grids!')
            
        
        self.loop_indices = find_loop_indices_HC(self.loop)
        self.neighbouring_loop_indices = find_adjacent_loop_indices(self.adjacency, self.loop, self.loop_indices)
        

    def start_new_game_even(self, start):
        self.index_tail = self.loop.index(start)
        self.index_head = self.loop.index(start)
        self.length = 1
        

    def find_path_even(self, location_apple):
        index_apple = self.loop_indices[location_apple]
        if self.length >= self.cutoff_length:
            yield from self.loop_and_not_track(index_apple)
            self.length += 1
            self.index_head = index_apple
            yield location_apple
        else:
            yield from self.greedy_skip(index_apple)
            self.length += 1
            yield location_apple

    # resort to looping, loses track of the tail
    # only use if you are committing to looping from now on
    def loop_and_not_track(self, index_apple):
        index_head = self.index_head
        loop = self.loop
        if index_head < index_apple:
            yield from islice(loop, index_head+1, index_apple)
            
        else:
            yield from chain(
                islice(loop, index_head+1, self.area),
                islice(loop, 0, index_apple)
            )

    # in case you have a variant where you decide to resort to looping for this move
    # but want to track the tail
    def loop_and_track(self, index_apple): 
        index_tail = self.index_tail
        index_head = self.index_head
        where_index_head_went = self.where_index_head_went
        loop = self.loop
        if index_head < index_apple:
            for new_index_head in range(index_head+1, index_apple):
                where_index_head_went[index_head] = new_index_head
                index_head = new_index_head
                index_tail = where_index_head_went[index_tail]
                yield loop[new_index_head]
        
        else:
            for new_index_head in chain(range(index_head+1, len(loop)), range(index_apple)):
                where_index_head_went[index_head] = new_index_head
                index_head = new_index_head
                index_tail = where_index_head_went[index_tail]
                yield loop[new_index_head]
            
        where_index_head_went[index_head] = index_apple
        self.index_head = index_apple
        self.index_tail = index_tail
    
    def greedy_skip(self, index_apple): 
        index_tail = self.index_tail
        index_head = self.index_head

        neighbouring_loop_indices = self.neighbouring_loop_indices
        area = self.area
        where_index_head_went = self.where_index_head_went
        loop = self.loop
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
                
                    if score > best_score:
                        best_new_index = possible_new_index

            where_index_head_went[index_head] = best_new_index 
            if best_new_index == index_apple:
                self.index_head = index_apple
                self.index_tail = index_tail
                break
            index_head = best_new_index 
            index_tail = where_index_head_went[index_tail]
            yield loop[best_new_index]

    def estimate_moves_per_apple_even(self):
        area = self.area
        pre_cutoff = [(apples_eaten) / 2 for apples_eaten in range(self.cutoff_length)]
        post_cutoff = [(area - apples_eaten) / 2 for apples_eaten in range(self.cutoff_length, area-1)]
        return pre_cutoff + post_cutoff
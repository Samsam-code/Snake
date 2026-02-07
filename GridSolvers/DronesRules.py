from GridSolvers.Templates import GridSolverTemplate_to_Loop
from GridsAndGraphs.Adjacencies import find_adjacency_AOW

class GridSolver_DronesRules(GridSolverTemplate_to_Loop):
    def __init__(self, m, n, name='Drone\'s Rules', cutoff='BEST GUESS'):
        if cutoff == 'BEST GUESS':
            const = 0.62    # looks good on the 32x32 grid
            cutoff = int( m * n * const)
        super().__init__(m, n, find_adjacency=find_adjacency_AOW, name=name, cutoff=cutoff)

    def find_and_commit_moves(self):
        carved_path = self.carved_path
        n = self.n

        tail = self.tail
        head = self.head
        apple = self.apple

        i_vector, j_vector = n, 1
        target_i, target_j = divmod(apple, n)
        i, j = divmod(head, n)
        i_even = i%2 == 0
        j_even = j%2 == 0

        while True:
            # select the first and second choice vectors by Drone's Rules
            if i_even:
                if j_even:
                    if target_j < j:
                        first_vector  = -j_vector
                        second_vector =  i_vector 
                    else:
                        first_vector  =  i_vector
                        second_vector = -j_vector 
                else:
                    if target_i < i:
                        first_vector  = -i_vector
                        second_vector = -j_vector
                    else:
                        first_vector  = -j_vector
                        second_vector = -i_vector
            else:
                if j_even:
                    if target_i > i:
                        first_vector  =  i_vector
                        second_vector =  j_vector
                    else:
                        first_vector  =  j_vector
                        second_vector =  i_vector
                else:
                    if target_j > j:
                        first_vector  =  j_vector
                        second_vector = -i_vector
                    else:
                        first_vector  = -i_vector
                        second_vector =  j_vector

            # prioritising the first choice over the second, choose a legal direction
            first_new_head = head + first_vector
            if carved_path[first_new_head] is None or first_new_head == tail:
                direction = first_vector
                new_head = first_new_head  
            else:
                # first direction is a collision
                direction = second_vector
                new_head = head + second_vector                   

            # exit if apple was hit
            if new_head == apple:
                carved_path[head] = apple
                self.tail = tail
                self.head = apple
                yield apple
                return           

            # update coordinates
            if direction == i_vector:
                i += 1
                i_even = not i_even
            elif direction == -i_vector:
                i -= 1
                i_even = not i_even
            elif direction == j_vector:
                j += 1
                j_even = not j_even
            else:
                j -= 1
                j_even = not j_even

            # commit the move
            carved_path[head] = new_head               
            head = new_head
            new_tail = carved_path[tail]
            carved_path[tail] = None
            tail = new_tail
            yield head

        # since only certain transitions are allowed between the states
        # this implementation *could* be slightly optimised
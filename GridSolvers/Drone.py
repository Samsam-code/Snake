from GridsAndGraphs.Adjacencies import find_grid_adjacency
class GridSolver_DronesRules():
    def __init__(self, m, n):
        self.m = m
        self.n = n
        self.area = m*n
        self.directions = (n, -n, 1, -1)
        self.adjacency = find_grid_adjacency(m, n)
        self.name = 'DronesRules'
        pass

    def start_new_game(self, start):
        self.i, self.j = divmod(start, self.n)
        self.occupied = [False] * self.area 
        self.occupied[start] = True
        self.direction_head_went = [None] * self.area 
        self.head = start
        self.tail = start

    def find_path(self, apple):
        head = self.head
        i, j = divmod(head, self.n)
        self.head = apple
        target_i, target_j = divmod(apple, self.n)
        i_even = i%2 == 0
        j_even = j%2 == 0

        i_vector, j_vector = self.n, 1

        while True:
            self.occupied[self.tail] = False
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

            if head+first_vector in self.adjacency[head] and not self.occupied[head+first_vector]:
                direction = first_vector
            else:
                direction = second_vector

            if direction == i_vector:
                i += 1
                i_even = not i_even
            elif direction == -i_vector:
                i -= 1
                i_even = not i_even
            elif direction == j_vector:
                j += 1
                j_even = not j_even
            elif direction == -j_vector:
                j -= 1
                j_even = not j_even

            self.direction_head_went[head] = direction
            head += direction
            self.occupied[head] = True
            
            if head == apple:
                self.occupied[self.tail] = True
            yield head
            self.tail += self.direction_head_went[self.tail]
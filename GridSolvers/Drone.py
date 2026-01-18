from GridsAndGraphs.Adjacencies import find_grid_adjacency_cell
class GridSolver_DronesRules():
    def __init__(self, m, n):
        self.m = m
        self.n = n
        self.area = m*n
        self.directions = (n, -n, 1, -1)
        self.adjacency = find_grid_adjacency_cell(m, n)
        self.name = 'DronesRules'

        self.UP = -n
        self.DOWN = n
        self.LEFT = -1
        self.RIGHT = 1

    def start_new_game(self, start):
        self.row, self.col = divmod(start, self.n)
        self.occupied = [False] * self.area 
        self.occupied[start] = True
        self.direction_head_went = [None] * self.area 
        self.head = start
        self.tail = start

    def find_path(self, apple):
        head = self.head
        row, col = divmod(head, self.n)
        self.head = apple
        target_row, target_col = divmod(apple, self.n)
        row_even = row%2 == 0
        col_even = col%2 == 0

        while True:
            self.occupied[self.tail] = False
            if row_even:
                if col_even:
                    if target_col < col:
                        first_vector  = self.LEFT
                        second_vector =  self.DOWN 
                    else:
                        first_vector  =  self.DOWN
                        second_vector = self.LEFT 
                else:
                    if target_row < row:
                        first_vector  = self.UP
                        second_vector = self.LEFT
                    else:
                        first_vector  = self.LEFT
                        second_vector = self.UP
            else:
                if col_even:
                    if target_row > row:
                        first_vector  =  self.DOWN
                        second_vector =  self.RIGHT
                    else:
                        first_vector  =  self.RIGHT
                        second_vector =  self.DOWN
                else:
                    if target_col > col:
                        first_vector  =  self.RIGHT
                        second_vector = self.UP
                    else:
                        first_vector  = self.UP
                        second_vector =  self.RIGHT

            if head+first_vector in self.adjacency[head] and not self.occupied[head+first_vector]:
                direction = first_vector
            else:
                direction = second_vector

            if direction == self.DOWN:
                row += 1
                row_even = not row_even
            elif direction == self.UP:
                row -= 1
                row_even = not row_even
            elif direction == self.RIGHT:
                col += 1
                col_even = not col_even
            elif direction == self.LEFT:
                col -= 1
                col_even = not col_even

            self.direction_head_went[head] = direction
            head += direction
            self.occupied[head] = True
            
            if head == apple:
                self.occupied[self.tail] = True
            yield head
            self.tail += self.direction_head_went[self.tail]
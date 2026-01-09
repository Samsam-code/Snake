from GridSpecificTools.DiveCycle import asym_dive_cycle_even

class GridSolver_AsymDive():
    def __init__(self, m, n, cutoff_length=None):
        if m%2 == 0:
            self.name = 'AsymDive'
            self.start_new_game = self.start_new_game_even
            self.find_path = self.find_path_even
        else:
            raise ValueError('AsymDive not yet implemented for odd amount of lines in the grid !')
        
        self.m = m
        self.n = n
        self.area = m * n
        self.loop = None
        self.cutoff_length = cutoff_length or self.area//2+2*self.m

    def start_new_game_even(self, start):
        self.snake_length = 1
        self.snake = [start]
        self.head = start
        self.head_coord = divmod(start, self.n)
        self.left_dives = [0]*(self.m//2-1)
        self.right_dives = [0]*(self.m//2-1)
        self.new_loop = True

    def find_path_even(self, apple):
        if self.new_loop:
            self.update_side()
            if self.snake_length < self.cutoff_length:
                self.decide_dive_lengths(divmod(apple, self.n))
            else:# self.snake_length == self.cutoff_length:
                lim = (self.head_coord[0]-1)//2 + 1 - self.is_left
                if self.is_left:
                    for i in range(lim):
                        self.right_dives[i] = self.n - self.left_dives[i] - 2
                    for i in range(lim, len(self.left_dives)):
                        self.left_dives[i] = self.n - self.right_dives[i] - 2
                else:
                    for i in range(lim):
                        self.left_dives[i] = self.n - self.right_dives[i] - 2
                    for i in range(lim, len(self.left_dives)):
                        self.right_dives[i] = self.n - self.left_dives[i] - 2
                self.new_loop = False

            self.loop = asym_dive_cycle_even(self.n, self.left_dives, self.right_dives)
            self.idx_head = self.loop.index(self.head)
            self.idx_bottom_right = 2*sum(self.left_dives) + self.m + self.n -3

        beg = self.idx_head+1
        idx_apple = self.loop.index(apple)
        end = idx_apple+1
        if beg < end:
            path = self.loop[beg:end]
        else:
            path = self.loop[beg:]+self.loop[:end]

        self.update_snake(path)
        self.idx_head = idx_apple
        return path

    def update_snake(self, path):
        self.snake_length += 1
        self.head = path[-1]
        self.head_coord = divmod(path[-1], self.n)

        p = len(path)
        if self.snake_length <= p:
            # Tail is entirely in path
            self.snake = path[-self.snake_length:]
        else:
            # Tail includes all of path + last part of snake
            need_from_snake = self.snake_length - p
            self.snake = self.snake[-need_from_snake:] + path

    def update_side(self):
        # if the snake lies on a single line, the side does not matter
        # except when it touches one edge
        if self.snake_length<self.n:
            # particular cases
            head_x, head_y = self.head_coord
            if head_x == 0:
                self.is_left = False
                return
            elif head_x == self.m -1:
                self.is_left = True
                return
            elif head_y == 0:
                self.is_left = True
                return
            elif head_y == self.n-1:
                self.is_left = False
                return
            elif head_x == self.snake[0]//self.n and abs(self.head-self.snake[0]) == self.snake_length-1:
                self.is_left = None
                return
        
        # otherwise, we just have to compare the index of the head 
        # to the index of the bottom right corner in the loop
        self.is_left = self.idx_head<=self.idx_bottom_right
    
    def decide_dive_lengths(self, apple_coords):
        """ Based on the position of the snake and the apple, find a good dive cycle to get to the apple quickly """
        head_x, head_y = self.head_coord
        apple_x, apple_y = apple_coords
        
        # Find out whether we will reach apple from left side or not
        if apple_y == 0: # Apple on left edge
            apple_is_left = True
        elif apple_y == self.n -1: # Apple on right edge
            apple_is_left = False
        elif head_x > apple_x: # Snake is below apple
            apple_is_left = False
        elif head_x < apple_x: # Snake is above apple
            apple_is_left = True
        elif head_x%2 == 0: # Snake and apple aligned and snake goes left
            apple_is_left = self.is_left and head_y>apple_y
        else: # Snake and apple aligned and snake goes right
            apple_is_left = self.is_left or head_y>apple_y

        idx_dive_apple = (apple_x-1)//2
        self.forget_some_dives(apple_coords, apple_is_left)
        
        idx_dive_head = (head_x-1)//2
        if self.is_left is None:
            # The snake forms a line so we decide to orient the snake in the fastest way to reach the apple
            self.is_left = apple_is_left
            if self.is_left:
                self.left_dives[idx_dive_head] = head_y
            else:
                self.right_dives[idx_dive_head] = self.n - head_y - 1

        if apple_x in (0,self.m-1) or apple_y in (0, self.n-1):
            # Apple is on an edge => stick to the edges
            return
        
        # Apple is inside the grid
        r_dive_apple = self.n - apple_y - 1
        if apple_is_left:
            if self.left_dives[idx_dive_apple]<apple_y:
                if self.right_dives[idx_dive_apple]< r_dive_apple:
                    self.left_dives[idx_dive_apple] = apple_y
                elif self.snake[0]//self.n == apple_x and self.snake[0]<apple_x*self.n+apple_y:
                    #Too dangerous to get that apple from the left side.
                    #Let the snake loop around and eat the apple from the right side
                    pass
                else:
                    # Apple in right part of the loop but that part is clear
                    # So reach the apple anyway
                    self.left_dives[idx_dive_apple] = apple_y
                    self.right_dives[idx_dive_apple] = r_dive_apple-1
        else:
            if self.right_dives[idx_dive_apple]< r_dive_apple:
                if self.left_dives[idx_dive_apple]< apple_y:
                    self.right_dives[idx_dive_apple] = r_dive_apple
                elif self.snake[0]//self.n == apple_x and self.snake[0]>apple_x*self.n+apple_y:
                    #Too dangerous to get that apple from the right side.
                    #Let the snake loop around and eat the apple from the left side
                    pass
                else:
                    # Apple in left part of the loop but that part is clear
                    # So reach the apple anyway
                    self.right_dives[idx_dive_apple] = r_dive_apple
                    self.left_dives[idx_dive_apple] = apple_y-1

    def forget_some_dives(self, apple_coords, apple_is_left):
        """ Delete as much dives as possible in a safe way """
        len_dives = self.m//2 -1
        if self.is_left is None or self.loop is None:
            self.left_dives = [0]*len_dives
            self.right_dives = [0]*len_dives
            return
        
        def reduce_dives(dive_list, margin, start, stop, step=1):
            for i in range(start, stop, step):
                if dive_list[i]>=margin:
                    dive_list[i] -= margin
                    return 0
                else:
                    margin -= dive_list[i]
                    dive_list[i] = 0
            return margin
        
        margin = (len(self.loop) - self.snake_length)//2
        if margin<=0:
            return
        
        head_x = self.head_coord[0]
        apple_x = apple_coords[0]
        idx_dive_head = (self.head_coord[0]-1)//2
        idx_dive_apple = (apple_coords[0]-1)//2
        if self.is_left:
            if apple_is_left:
                end_offset = 1-apple_x%2
                if apple_x<head_x:
                    # Edge case in the early game where an apple spawns on the left edge of the grid above the snake
                    # In this case the snake has to do almost an entire loop
                    margin = reduce_dives(self.left_dives, margin, idx_dive_head+1, len_dives)
                    margin = reduce_dives(self.right_dives, margin, len_dives-1, -1, -1)
                    reduce_dives(self.left_dives, margin, 0,  idx_dive_apple+end_offset)
                else:
                    reduce_dives(self.left_dives, margin, idx_dive_head+1, idx_dive_apple+end_offset)
            else:
                end_offset = apple_x%2
                margin = reduce_dives(self.left_dives, margin, idx_dive_head+1, len_dives)
                reduce_dives(self.right_dives, margin, len_dives-1, idx_dive_apple-end_offset,-1)
        else:
            if apple_is_left:
                end_offset = 1-apple_x%2
                margin = reduce_dives(self.right_dives, margin, idx_dive_head-1, -1, -1)
                reduce_dives(self.left_dives, margin, 0,  idx_dive_apple+end_offset)
            else:
                end_offset = apple_x%2
                if apple_x>head_x:
                    # Similar than above
                    margin = reduce_dives(self.right_dives, margin, idx_dive_head-1, -1, -1)
                    margin = reduce_dives(self.left_dives, margin, 0, len_dives)
                    reduce_dives(self.right_dives, margin, len_dives-1, idx_dive_apple-end_offset,-1)
                else: 
                    reduce_dives(self.right_dives, margin, idx_dive_head-1, idx_dive_apple-end_offset,-1)
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
                self.decide_dive_lengths(apple)
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
            elif head_x == self.snake[0]//self.n:
                self.is_left = None
                return
        
        # otherwise, we just have to compare the index of the head 
        # to the index of the bottom right corner in the loop
        self.is_left = self.idx_head<=self.idx_bottom_right
    
    def decide_dive_lengths(self, apple):
        """ Based on the position of the snake and the apple, find a good dive cycle to get to the apple quickly """
        head_x, head_y = self.head_coord
        apple_x, apple_y = divmod(apple, self.n)
        
        # Find out whether we will reach apple from left side or not
        if apple_y == 0: # Apple on left edge
            reach_apple_from_left_side = True
        elif apple_y == self.n -1: # Apple on right edge
            reach_apple_from_left_side = False
        elif head_x > apple_x: # Snake is below apple
            reach_apple_from_left_side = False
        elif head_x < apple_x: # Snake is above apple
            reach_apple_from_left_side = True
        elif head_x%2 == 0: # Snake and apple aligned and snake goes left
            reach_apple_from_left_side = self.is_left and head_y>apple_y
        else: # Snake and apple aligned and snake goes right
            reach_apple_from_left_side = self.is_left or head_y>apple_y

        idx_dive_apple = (apple_x-1)//2
        self.forget_some_dives(idx_dive_apple, reach_apple_from_left_side)
        
        idx_dive_head = (head_x-1)//2
        if self.is_left is None:
            # The snake forms a line so we decide to orient the snake in the fastest way to reach the apple
            self.is_left = apple>self.head
            if self.is_left:
                self.left_dives[idx_dive_head] = head_y
            else:
                self.right_dives[idx_dive_head] = self.n - head_y - 1

        if apple_x in (0,self.m-1) or apple_y in (0, self.n-1):
            # Apple is on an edge => stick to the edges
            return
        
        r_dive_apple = self.n - apple_y - 1
        if self.left_dives[idx_dive_apple]<apple_y and self.right_dives[idx_dive_apple]< r_dive_apple:
            # Apple is inside the grid
            if reach_apple_from_left_side:
                self.left_dives[idx_dive_apple] = apple_y
            else:
                self.right_dives[idx_dive_apple] = r_dive_apple

    def forget_some_dives(self, idx_apple, reach_apple_from_left_side):
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
        
        idx_head = (self.head_coord[0]-1)//2
        if self.is_left:
            if reach_apple_from_left_side:
                reduce_dives(self.left_dives, margin, idx_head+1, idx_apple)
            else:
                margin = reduce_dives(self.left_dives, margin, idx_head+1, len_dives)
                reduce_dives(self.right_dives, margin, len_dives-1, idx_apple,-1)
        else:
            if reach_apple_from_left_side:
                margin = reduce_dives(self.right_dives, margin, idx_head-1, -1, -1)
                reduce_dives(self.left_dives, margin, 0,  idx_apple)
            else:
                reduce_dives(self.right_dives, margin, idx_head-1, idx_apple,-1)
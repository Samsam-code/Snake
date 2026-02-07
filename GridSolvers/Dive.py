from GridsAndGraphs.DiveCycle import dive_cycle_even

class GridSolver_Dive():
    def __init__(self, m, n):
        if m%2 == 0:
            self.name = 'Dive'
            self.start_new_game = self.start_new_game_even
            self.find_path = self.find_path_even
        else:
            raise ValueError('Dive not yet implemented for odd amount of lines in the grid !')
        
        self.m = m
        self.n = n
        self.area = m * n
        self.loop = None

    def yield_moves_to_simulator(self, start):
        self.start_new_game(start)
        while True:
            yield from self.find_path(self.apple)

    def start_new_game_even(self, start):
        self.snake_length = 1
        self.snake = [start]
        self.head = divmod(start, self.n)
        self.dive_lengths = [None]*(self.m//2-1)
        self.is_left = None

    def find_path_even(self, apple):
        if None in self.dive_lengths:
            # There is some degree of freedom for the loop
            if self.is_left is None:
                # The snake forms a line so we decide to orient the snake in the fastest way to reach the apple
                self.is_left = apple>self.snake[-1]

            dive_lengths = self.decide_dive_lengths(apple)
            self.loop = dive_cycle_even(self.n, dive_lengths)
            self.idx_head = self.loop.index(self.snake[-1])
            self.idx_bottom_right = 2*sum(dive_lengths) + self.m + self.n -3
        else:
            # No degree of freedom, use the same loop as before
            dive_lengths = self.dive_lengths

        beg = self.idx_head+1
        idx_apple = self.loop.index(apple)
        end = idx_apple+1
        if beg < end:
            path = self.loop[beg:end]
        else:
            path = self.loop[beg:]+self.loop[:end]

        self.update_snake(path)
        self.idx_head = idx_apple
        self.update_side()
        self.update_dive_lengths(dive_lengths)
        return path

    def update_snake(self, path):
        self.snake_length += 1
        self.head = divmod(path[-1], self.n)

        p = len(path)
        if self.snake_length <= p:
            # Tail is entirely in path
            self.snake = path[-self.snake_length:]
        else:
            # Tail includes all of path + last part of snake
            need_from_snake = self.snake_length - p
            self.snake = self.snake[-need_from_snake:] + path

    def update_side(self):
        head_x, head_y = self.head
        if head_x == 0:
            self.is_left = False
            return
        elif head_x == self.m -1:
            self.is_left = True
            return
        # if the snake lies on a single line, the side does not matter
        # except when it touches one edge
        elif self.snake_length<self.n:
            # particular cases
            if head_y == 0:
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
        head_x, head_y = self.head
        apple_x, apple_y = divmod(apple, self.n)
        dives = self.dive_lengths.copy()
        if apple_x in (0,self.m-1) or apple_y in (0, self.n-1):
            # Apple is on an edge
            if head_x > apple_x:
                # Snake is below apple
                for i in range(len(dives)):
                    if dives[i] is None:
                        dives[i] = self.n-2
            else:
                # Snake is above apple
                for i in range(len(dives)):
                    if dives[i] is None:
                        dives[i] = 0 
        else:
            # Apple is inside the grid
            idx_dive_apple = (apple_x-1)//2
            if head_x> apple_x:
                # Snake is below apple => reach apple from right side
                if dives[idx_dive_apple] is None:
                    dives[idx_dive_apple] = apple_y-1
                for i in range(len(dives)):
                    if dives[i] is None:
                        dives[i] = self.n-2
            else:
                # Snake is above apple => reach apple from the left side
                if dives[idx_dive_apple] is None:
                    dives[idx_dive_apple] = apple_y
                for i in range(len(dives)):
                    if dives[i] is None:
                        dives[i] = 0

        # Safeguard: Make sure the snake does not jump from left side to right sides
        if head_x not in (0, self.m-1) and head_y not in (0, self.n-1):
            idx_dive_head = (head_x-1)//2
            if self.is_left:
                if dives[idx_dive_head]< head_y:
                    dives[idx_dive_head] = head_y
            else:
                if dives[idx_dive_head]>= head_y:
                    dives[idx_dive_head] = head_y-1
            
        return dives
 
    def update_dive_lengths(self, dive_lengths):
        """
        Based on the loop given by ``dive_lengths``, update ``self.dive_lengths`` such that 
        it contains the minimal amount of dives the snake is currently following
        The other dives are set to ``None`` (so that they can be replaced by any value you want)
        """
        if self.is_left is None:
            return
        
        def consume_dive(idx, to_remove, l):
            l -= to_remove 
            if l > 0: 
                self.dive_lengths[idx] = dive_lengths[idx] 
                l -= to_remove 
            return l

        len_dives = self.m//2 -1
        self.dive_lengths = [None]*len_dives

        l = self.snake_length
        head_x, head_y = self.head
        idx_x = (head_x-1)//2

        if self.is_left:  
            if head_x%2 == 0:
                head_y_gap = head_y
                l = consume_dive(idx_x, dive_lengths[idx_x]+1, l+head_y_gap)
            else:
                l-= head_y + 1
                if head_x == self.m-1:
                    head_y_gap = self.n - head_y - 1
                else:
                    head_y_gap = dive_lengths[idx_x] -head_y

            idx_x -=1
            while l> 0 and idx_x>=0:
                l = consume_dive(idx_x, dive_lengths[idx_x]+1, l)
                idx_x -= 1

            l = self.snake_length - self.n*(head_x+1) + head_y_gap
            if l <= 0 or head_x >= self.m-2:
                return
            
            idx_x = head_x//2
            if head_x%2 == 1:
                l -= self.n - dive_lengths[idx_x] -1
                self.dive_lengths[idx_x] = dive_lengths[idx_x]
                idx_x+=1
            
            while l>0 and idx_x<len_dives:
                l = consume_dive(idx_x, self.n - dive_lengths[idx_x] -1, l)
                idx_x +=1
            return
        else:
            if head_x%2 == 1:
                head_y_gap = self.n - head_y - 1
                l = consume_dive(idx_x, self.n - dive_lengths[idx_x] - 1, l+head_y_gap)
            else:
                l-= self.n - head_y
                if head_x == 0:
                    head_y_gap = head_y 
                else:
                    head_y_gap = head_y - dive_lengths[idx_x] - 1
                    
            idx_x +=1
            while l> 0 and idx_x<len_dives:
                l = consume_dive(idx_x, self.n - dive_lengths[idx_x] -1, l)
                idx_x += 1

            l = self.snake_length - self.n*(self.m - head_x) + head_y_gap
            if l <= 0 or head_x <= 1:
                return

            idx_x = head_x//2 -1
            if head_x%2 == 0:
                l -= dive_lengths[idx_x] +1
                self.dive_lengths[idx_x] = dive_lengths[idx_x]
                idx_x-=1
            
            while l>0 and idx_x>=0:
                l = consume_dive(idx_x, dive_lengths[idx_x]+1, l)
                idx_x -=1
            return
            
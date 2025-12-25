from GridSpecificTools.DiveCycle import asym_dive_cycle_even

class GridSolver_AsymDive():
    def __init__(self, m, n):
        if m%2 == 0:
            self.name = 'AsymDive Even'
            self.start_new_game = self.start_new_game_even
            self.find_path = self.find_path_even
        else:
            raise ValueError('AsymDive not yet implemented for odd amount of lines in the grid !')
        
        self.m = m
        self.n = n
        self.area = m * n
        self.loop = None

    def start_new_game_even(self, start):
        self.snake_length = 1
        self.snake = [start]
        self.head = divmod(start, self.n)
        self.left_dives = [0]*(self.m//2-1)
        self.right_dives = [0]*(self.m//2-1)
        self.is_left = None

    def find_path_even(self, apple):
        #if None in self.left_dives or None in self.right_dives:
            # There is some degree of freedom for the loop
        if self.is_left is None:
            # The snake forms a line so we decide to orient the snake in the fastest way to reach the apple
            self.is_left = apple>self.snake[-1]

        left_dives, right_dives = self.decide_dive_lengths(apple)
        self.loop = asym_dive_cycle_even(self.n, left_dives, right_dives)
        self.idx_head = self.loop.index(self.snake[-1])
        self.idx_bottom_right = 2*sum(left_dives) + self.m + self.n -3
        #else:
            # No degree of freedom, use the same loop as before
        #    left_dives, right_dives = self.left_dives, self.right_dives

        beg = self.idx_head+1
        try:
            idx_apple = self.loop.index(apple)
        except ValueError as e:
            print("apple not in loop")
            raise e
        end = idx_apple+1
        if beg < end:
            path = self.loop[beg:end]
        else:
            path = self.loop[beg:]+self.loop[:end]

        self.update_snake(path)
        self.idx_head = idx_apple
        self.update_side()
        self.update_dive_lengths(left_dives, right_dives)
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
        left_dives = self.left_dives.copy()
        right_dives = self.right_dives.copy()
        if apple_x in (0,self.m-1) or apple_y in (0, self.n-1):
            # Apple is on an edge => stick to the edges
            pass
        else:
            idx_dive_apple = (apple_x-1)//2
            dive = self.n - apple_y - 1
            # Apple is inside the grid
            if head_x> apple_x:
                # Snake is below apple => reach apple from right side
                if left_dives[idx_dive_apple]<apple_y and right_dives[idx_dive_apple]< dive:
                    right_dives[idx_dive_apple] = dive
            else:
                # Snake is above apple => reach apple from the left side
                if right_dives[idx_dive_apple]<dive and left_dives[idx_dive_apple]< apple_y:
                    left_dives[idx_dive_apple] = apple_y

        # Safeguard: Make sure the snake does not jump from left side to right sides
        if head_x not in (0, self.m-1) and head_y not in (0, self.n-1):
            idx_dive_head = (head_x-1)//2
            if self.is_left:
                left_dives[idx_dive_head] = max(left_dives[idx_dive_head], head_y)
                right_dives[idx_dive_head] = min(right_dives[idx_dive_head], self.n - head_y - 2)
            else:
                left_dives[idx_dive_head] = min(left_dives[idx_dive_head], head_y-1)
                right_dives[idx_dive_head] = max(right_dives[idx_dive_head], self.n - head_y - 1)
            
        # Widen dives if necessary
        loop_length = 2*(self.m + self.n -2) + sum(left_dives) + sum(right_dives)
        #if self.snake_length > loop_length:
        #input(self.snake_length - loop_length)
        
        return left_dives, right_dives
 
    def update_dive_lengths(self, left_dives, right_dives):
        """
        Based on the loop given by ``dive_lengths``, update ``self.dive_lengths`` such that 
        it contains the minimal amount of dives the snake is currently following
        The other dives are set to ``None`` (so that they can be replaced by any value you want)
        """
        if self.is_left is None:
            return

        def consume_dive(dives, out, idx, l):
            l -= dives[idx] + 1 
            if l > 0: 
                out[idx] = dives[idx] 
                l -= dives[idx] + 1 
            return l

        len_dives = self.m//2 -1
        self.left_dives = [0]*len_dives
        self.right_dives = [0]*len_dives

        l = self.snake_length
        head_x, head_y = self.head
        idx_x = (head_x-1)//2

        if self.is_left:  
            if head_x%2 == 0:
                head_y_gap = head_y
                l = consume_dive(left_dives, self.left_dives, idx_x, l+head_y_gap)
            else:
                l-= head_y + 1
                if head_x == self.m-1:
                    head_y_gap = self.n - head_y - 1
                else:
                    head_y_gap = left_dives[idx_x] -head_y

            idx_x -=1
            while idx_x>=0:
                l = consume_dive(left_dives, self.left_dives, idx_x, l)
                if l<= 0:
                    return
                idx_x -= 1
            
            l -= self.n
            idx_x = 0
            while idx_x<len_dives:
                l = consume_dive(right_dives, self.right_dives, idx_x, l)
                if l <= 0:
                    return
                idx_x += 1

            l -= self.n
            idx_x = len_dives-1
            while idx_x>=0 and l>0:
                l = consume_dive(left_dives, self.left_dives, idx_x, l)
                idx_x -= 1

            if idx_x < len_dives-1:
                self.left_dives[idx_x+1] = left_dives[idx_x+1]
        else:
            if head_x%2 == 1:
                head_y_gap = self.n - head_y - 1
                l = consume_dive(right_dives, self.right_dives, idx_x, l + head_y_gap)
            else:
                l-= self.n - head_y
                if head_x == 0:
                    head_y_gap = head_y 
                else:
                    head_y_gap = head_y - self.n + right_dives[idx_x]
                    
            idx_x +=1
            while idx_x<len_dives:
                l = consume_dive(right_dives, self.right_dives, idx_x, l)
                if l<= 0:
                    return
                idx_x += 1
            
            l -= self.n
            idx_x = len_dives -1
            while idx_x>=0:
                l = consume_dive(left_dives, self.left_dives, idx_x, l)
                if l<= 0:
                    return
                idx_x -= 1

            l -= self.n
            idx_x = 0
            while idx_x>=0 and l>0:
                l = consume_dive(right_dives, self.right_dives, idx_x, l)
                idx_x += 1
            
            if idx_x > 0:
                self.right_dives[idx_x-1] = right_dives[idx_x-1]

            return
            
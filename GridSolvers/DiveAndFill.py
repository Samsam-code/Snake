

class GridSolver_DiveAndFill():
    def __init__(self, m, n):
        if not m%2 == 0:
            raise ValueError('Not implemented for odd number of rows')

        self.name = 'DiveAndFill'
        self.area = m*n
        self.index_to_coords = [divmod(x, n) for x in range(self.area)]

        self.m = m
        self.n = n
    
    def yield_moves_to_simulator(self, start):
        self.start_new_game(start)
        while True:
            yield from self.find_path(self.apple)

    def start_new_game(self, start):
        
        self.head = start
        self.length = 0
        self.move_counter = 0
        self.dive_depths = [0] * self.m
        self.last_occupied = [0] * self.area

        
        self.snake_blocking_this_row = False
        i_start, j_start = self.index_to_coords[start]

        if i_start == 0 or j_start < self.n-1:
            self.dive_is_from_left = True
            self.short_vector = 1
            self.long_vector = self.n
        
        else:
            self.dive_is_from_left = False
            self.short_vector = -1
            self.long_vector = -self.n

    def find_path(self, apple):
        self.length += 1    
        head = self.head
        for head in self.first_decision(head, apple):
            self.commit_move(head)
            yield head

        
        n = self.n
        i_apple, j_apple = self.index_to_coords[apple]

        if self.snake_blocking_this_row:
            for head in self.space_filling_mode(head, apple):
                self.commit_move(head)
                yield head

        while True:
        
            # check if we should dive from the other side - need to do only once
            i_head,  j_head  = self.index_to_coords[head]
            if self.dive_is_from_left:
                apple_is_behind_head = i_apple < i_head
                apple_is_on_other_side = j_apple == n-1
            else:
                apple_is_behind_head = i_apple > i_head
                apple_is_on_other_side = j_apple == 0

            if apple_is_behind_head or apple_is_on_other_side:
                for head in self.swing_to_other_side(head):
                    self.commit_move(head)
                    yield head

                # we now have some snake body ahead of us, in principle, so we must fill in space
                for head in self.space_filling_mode(head, apple):
                    self.commit_move(head)
                    yield head
                continue
            break

            

        # getting this far tells us:
        # - head is on edge, in diving position
        # - apple is in front of head
        # - apple can be reached from this side
        # - entire snake is behind head

        # calculate entrance to rung holding apple
        i_head, j_head = self.index_to_coords[head]
        depth = abs(j_head - j_apple)
        if self.dive_is_from_left:
            i_dive = i_apple - 1 + i_apple % 2         
        else:
            i_dive = i_apple + i_apple % 2 
        distance_to_entrance = abs(i_head - i_dive)
        
        # catch up to that entrance
        long_vector = self.long_vector
        for _ in range(distance_to_entrance):
                head += long_vector
                self.commit_move(head)
                yield head

        # dive in to meet the apple
        self.dive_depths[i_dive] = depth
        for head in self.insert_dive(head, depth):
            self.commit_move(head)
            yield head
        return

    def space_filling_mode(self, head, apple):
        short_vector = self.short_vector
        long_vector = self.long_vector
        i_head, j_head = self.index_to_coords[head]
        n = self.n

        across_exit = head + short_vector * (n - 1)
        while True:
            tail_counter = self.move_counter - self.length + 1
            number_of_moves_until_row_clear = self.last_occupied[across_exit] - tail_counter
            snake_blocking_this_row = number_of_moves_until_row_clear > n-1
            if not snake_blocking_this_row:
                break
            depth = self.n - 2 - self.dive_depths[i_head+short_vector]
            # fill the space with snake, to avoid bad apples
            self.dive_depths[i_head] = depth
            yield from self.insert_dive(head, depth)
            # shidt up by two rows and repeat
            i_head      += 2 * short_vector
            head        += 2 * long_vector
            across_exit += 2 * long_vector
            continue
            
        # if this row does have an apple, the snake may still be an obstacle as it won't move as much
        i_apple, j_apple = self.index_to_coords[apple]
        apple_in_this_row = (i_apple == i_head) and apple != across_exit
        if apple_in_this_row:
            # dive to meet the apple, unless it is on other side
            depth = abs(j_apple - j_head) 
            if depth < self.n-1:
                self.dive_depths[i_head] = depth
                yield from self.insert_dive(head, depth)
                return
                # this will hit the apple so we are cut off here

            

        # otherwise, the entire snake is effectively behind us, so forget all divelengths ahead of us
        self.snake_blocking_this_row = False
        i_final = self.m-1 if self.dive_is_from_left else 0
        for i in range(i_head, i_final + short_vector, short_vector):
            self.dive_depths[i] = 0

        
    def first_decision(self, head, apple):
        # get the snake to the apple if in thi dive, 
        # else get it to the next diving position,
        # and return to the main logic

        i_head, j_head = self.index_to_coords[head]
        n = self.n

        # if we are on either end, then we should wrap around
        if i_head in (0, n-1):
            self.snake_blocking_this_row = True
            if i_head == 0:
                self.dive_is_from_left = True
                self.short_vector = 1
                self.long_vector = n
                distance_to_edge = j_head
            else:
                self.dive_is_from_left = False
                self.short_vector = -1
                self.long_vector = -n
                distance_to_edge = n-1-j_head
            for _ in range(distance_to_edge):
                head -= self.short_vector
                yield head
            head += self.long_vector
            yield head
            return
        
        short_vector = self.short_vector
        long_vector = self.long_vector
        if self.dive_is_from_left:
            is_in_dive_row = i_head % 2 == 1
            j_this_edge = 0
            j_far_edge = n-1
        else:
            is_in_dive_row = i_head % 2 == 0
            j_this_edge = n - 1
            j_far_edge = 0

        if is_in_dive_row:
            # we have some decisions to make...
            
            # if apple is in this dive, we might be able to extend dive to get it
            i_apple, j_apple = self.index_to_coords[apple]
            apple_depth = abs(j_apple - j_this_edge)
            head_depth  = abs(j_head  - j_this_edge)

            if i_apple == i_head and j_apple != j_far_edge and head_depth < apple_depth:
                # apple a little further, walk to it
                self.dive_depths[i_head] = apple_depth
                for _ in range(apple_depth - head_depth):
                    head += short_vector
                    yield head
                return
            
            # if the snake is blocking our path, we should fill in this space
            if self.snake_blocking_this_row:
                across_exit = head - j_head + j_far_edge
                distance_to_other_edge = abs(j_head - j_far_edge)
                tail_counter = self.move_counter - self.length + 1
                number_of_moves_until_row_clear = self.last_occupied[across_exit] - tail_counter
                snake_blocking_this_row = number_of_moves_until_row_clear > distance_to_other_edge

                if snake_blocking_this_row:
                    across_depth = self.dive_depths[i_head + short_vector]
                    new_depth = self.n - 2 - across_depth
                    
                    self.dive_depths[i_head] = new_depth
                    for head_depth in range(head_depth+1, new_depth+1):
                        j_head += short_vector
                        head += short_vector
                        yield head

                else:
                    # otherwise, the entire snake is effectively behind us, so forget all divelengths ahead of us
                    self.snake_blocking_this_row = False
                    i_final = self.m-1 if self.dive_is_from_left else 0
                    self.dive_depths[i_head] = head_depth
                    for i in range(i_head + short_vector, i_final + short_vector, short_vector):
                        self.dive_depths[i] = 0
            
            elif i_apple == i_head + short_vector and apple_depth > head_depth and j_apple != j_far_edge:
                # apple a little further, and one up, walk to it
                self.dive_depths[i_head] = apple_depth
                for head_depth in range(head_depth+1, apple_depth+1):
                    j_head += short_vector
                    head += short_vector
                    yield head

            # go up one to the return row, and follow other logic
            head += long_vector
            yield head
            
        # now we are in the return row, off we go to the next dive position
        depth = abs(j_head - j_this_edge)
        for _ in range(depth):
            head -= short_vector
            yield head
        head += long_vector
        yield head
        return 


    def commit_move(self, head):
        self.head = head
        self.move_counter += 1
        self.last_occupied[head] = self.move_counter


    def insert_dive(self, head, depth):
        # record the dive in self.dive_depth before calling this!
        short_vector = self.short_vector
        long_vector = self.long_vector

        # go as deep as possible, turn around, come back
        for _ in range(depth):
            head += short_vector
            yield head
        head += long_vector
        yield head
        for _ in range(depth):
            head -= short_vector
            yield head
        head += long_vector
        yield head
        
    
    def swing_to_other_side(self, head):
        long_vector  = self.long_vector
        i_final = self.m-1 if self.dive_is_from_left else 0
        j_final = self.n-1 if self.dive_is_from_left else 0
        # go to last row
        i_head, j_head = self.index_to_coords[head]
        for _ in range(abs(i_head - i_final)):
            head += long_vector
            yield head
         # we are now on other side
        self.short_vector *= -1
        self.long_vector  *= -1
        self.snake_blocking_this_row = True
        self.dive_is_from_left = not self.dive_is_from_left

        #  go to end of last row
        for _ in range(abs(j_head - j_final)):
            head -= self.short_vector
            yield head
       
        # take one step forward, so we are in a diving position
        head += self.long_vector
        yield head

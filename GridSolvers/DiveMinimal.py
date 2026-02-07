"""
A flawed implementation of the DiveMinimal strategy
Follow the perimeter of the Dive directed subgraph, 
diving only to avoid a collision or to collect an apple
"""

class GridSolver_DiveMinimal:
    def __init__(self, m, n):
        if not m%2 == 0:
            raise ValueError('Not implemented for odd number of rows')

        self.name = 'DiveMinimal'
        self.area = m*n
        self.index_to_coords = [divmod(x, n) for x in range(self.area)]

        self.m = m
        self.n = n

    def yield_moves_to_simulator(self, start):
        self.start_new_game(start)
        while True:
            yield from self.find_path(self.apple)

    def estimate_moves_per_apple(self):
        area = self.area
        return [apples_eaten / 3 for apples_eaten in range(area-1)]
        

    def start_new_game(self, start):
        self.head = start
        self.length = 0
        self.move_counter = 0
        self.dive_depths = [0] * self.m
        self.last_occupied = [0] * self.area

        self.snake_blocking_this_row = False
        i_start, j_start = self.index_to_coords[start]
        if i_start < self.n-1 and j_start < self.n-1:
            self.dive_is_from_left = True
            self.short_vector = 1
            self.long_vector = self.n
        else:
            self.dive_is_from_left = False
            self.short_vector = -1
            self.long_vector = -self.n


    def find_path(self, apple):
        self.length += 1
        i_apple, j_apple = self.index_to_coords[apple]


        # can we extend current dive to go to apple?
        # if not, go to next dive position
        for head in self.first_decision(apple):
            self.commit_move(head)
            yield head

        # orbit until we can dive for the apple
        while True:
            head = self.head
            i_head,  j_head  = self.index_to_coords[head]

            if self.dive_is_from_left:
                j_other_side = self.n - 1
                i_final = self.m - 1
                apple_is_ahead = i_apple >= i_head
            else:
                j_other_side = 0
                i_final = 0
                apple_is_ahead = i_apple <= i_head
        
            apple_on_this_side = i_apple != i_final and j_apple != j_other_side
            if apple_is_ahead and apple_on_this_side:
                # we can reach the apple without wrapping around again!
                break

            # otherwise go to top, wrap around, and try again
            num_dives = abs(i_final - i_head) // 2
            for head in self.avoid_collisions(head, num_dives):
                self.commit_move(head)
                yield head
            for head in self.swich_sides_at_end(head):
                self.commit_move(head)
                yield head
            
        # catch up to rung holding apple, and dive to get it
        if self.dive_is_from_left:
            i_dive = i_apple - 1 + i_apple % 2
        else:
            i_dive = i_apple + i_apple % 2
        num_dives = abs(i_dive - i_head) // 2
        for head in self.avoid_collisions(head, num_dives):
            self.commit_move(head)
            yield head
        apple_depth = abs(j_apple - j_head)
        for head in self.insert_dive(head, apple_depth):
            self.commit_move(head)
            yield head
        

    def first_decision(self, apple):
        head = self.head
        i_head,  j_head  = self.index_to_coords[head]

        switch_to_right = self.dive_is_from_left and i_head == self.n - 1
        switch_to_left  = not self.dive_is_from_left and i_head == 0

        if switch_to_right or switch_to_left:
            self.dive_is_from_left = not self.dive_is_from_left
            self.short_vector *= -1
            self.long_vector  *= -1


        i_apple, j_apple = self.index_to_coords[apple]
        
        short_vector = self.short_vector
        long_vector = self.long_vector

        head_in_dive_row = i_head % 2 == 1 if self.dive_is_from_left else i_head %2 == 0
        j_this_side = 0 if self.dive_is_from_left else self.n-1
        j_far_side  = self.n-1 if self.dive_is_from_left else 0

        if head_in_dive_row:

            if i_apple == i_head and j_apple != j_far_side:
                apple_is_ahead = j_apple > j_head if self.dive_is_from_left else j_apple < j_head
                if apple_is_ahead:
                    for head in range(head+short_vector, apple+short_vector, short_vector):
                        yield head
                    return
            
            elif i_apple == i_head + short_vector and j_apple != j_far_side:
                apple_is_behind = j_apple <= j_head if self.dive_is_from_left else j_apple >= j_head
                if apple_is_behind:
                    for head in range(head+long_vector, apple-short_vector, -short_vector):
                        yield head
                    return
                else:
                    turn_below_apple = apple - long_vector
                    distance_to_turn = abs(j_head - j_apple)
                    tail_counter = self.move_counter - self.length + 1
                    turn_will_be_free = self.last_occupied[turn_below_apple] < tail_counter + distance_to_turn
                    if turn_will_be_free:
                        for head in range(head+short_vector, turn_below_apple+short_vector, short_vector):
                            yield head
                        yield apple
            else:
                exit = head + self.long_vector
                tail_counter = self.move_counter - self.length + 1
                moves_until_exit_clear = self.last_occupied[exit] - tail_counter 
                necessary_dive_depth = max(0, (moves_until_exit_clear + 1) // 2)
                for _ in range(necessary_dive_depth):
                    head += short_vector
                    j_head += short_vector
                    yield head
                head += long_vector
                yield head

        # we are now in the return row. go to end, and go up one to next diving position
        for _ in range(abs(j_head - j_this_side)):
            head -= short_vector
            yield head
        head += long_vector

        yield head

    def swich_sides_at_end(self, head):
        # face the other way
        self.dive_is_from_left = not self.dive_is_from_left
        self.short_vector *= -1
        self.long_vector  *= -1
        # 'come back' to other side
        for head in range(head-self.short_vector, head - self.short_vector * self.n, -self.short_vector):
            yield head
        head += self.long_vector
        yield head

    def avoid_collisions(self, head, num_dives):
        for _ in range(num_dives):
            for head in self.find_minimum_dive_to_avoid_collision(head):
                yield head

    def find_minimum_dive_to_avoid_collision(self, head):
        exit = head + self.long_vector
        tail_counter = self.move_counter - self.length + 1
        moves_until_exit_clear = self.last_occupied[exit] - tail_counter 
        necessary_dive_depth = max(0, (moves_until_exit_clear + 1) // 2)
        yield from self.insert_dive(head, necessary_dive_depth)
        

    def insert_dive(self, head, depth):
        # record the dive in self.dive_depth before calling this!
        short_vector = self.short_vector
        long_vector = self.long_vector

        # go as deep as necessary, turn around, come back, go up one to start next dive position
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


    def commit_move(self, head):
        self.head = head
        self.move_counter += 1
        self.last_occupied[head] = self.move_counter
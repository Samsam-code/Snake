import time
import heapq
from fractions import Fraction


class SnakeNode():
    """
    A class for the node of SnakeTree
    """
    def __init__(self, value, parent):
        self.value    = value
        self.parent   = parent
        self.children = {}

    def add_child(self, value):
        child = SnakeNode(value, self)
        self.children[value] = child
        return child
    
    def __lt__(self, other):
        """x < y unless x = y"""
        # this is a dodgy fix 
        # so that we can priority queue tuples
        # containing a node
        return self is not other
    

class SnakeTree():
    """
    A class of basic methods for Tries storing snakes 
    (self-avoiding walks) on a graph.
    """
    # Of which we use maybe one or two
    # but nice to have it centralised

    def __init__(self):
        self.root = SnakeNode(None, None)

        self.start_time = time.time()
        self.time       = self.start_time
        self.total_time = 0

    def find_snake(self, node):
        """Given node, finds the snake"""
        lst = []
        while node is not self.root:
            lst.append(node.value)
            node = node.parent
        return tuple(reversed(lst))
    
    def find_node(self, snake):
        """Given snake, finds the node, if it exists"""
        node = self.root
        for x in snake:
            if x not in node.children:
                return None
            node = node.children[x]
        return node
    
    def delete_node(self, node):
        """Prunes tree to remove the node"""
        parent = node.parent
        while parent.children:
            del parent.children[node.value]
            node.parent = None
            node = parent
            parent = node.parent

    def add_snake(self, snake):
        """Given snake, finds the node, creating it if necessary."""
        node = self.root
        for i, x in enumerate(snake):
            if x not in node.children:
                break
            node = node.children[x]
        else:
            return node
        for x in snake[i:]:
            node = node.add_child(x)
        return node
    
    def count_nodes(self):
        count = 0
        stack = [self.root]
        for node in stack:
            for child in node.children:
                stack.append(node.children[child])
                count += 1
        self.num_nodes = count

    def update_time(self):
        t = time.time()
        step  = t - self.time
        total = t - self.start_time
        self.time = t
        return step, total


class SafeWinningSnakeTree(SnakeTree):
    """
    The Trie of the snakes that a safe strategy may end the game in.
    They form a subset of the Hamiltonian Paths
    and include all Hamiltonian Cycles.
    """

    def __init__(self, adjacency):
        super().__init__()
        self.adjacency = adjacency      # a list of the neighbours of each vertex of the graph
        self.area = len(adjacency)      # the number of vertices in the graph
    
    def grow_safe_winning_snakes(self, printing=False):
        # we use a depth-first search
        # keeping track of the possible edges, degrees, occupancy
        # exiting early if no safe winning snake is possible
        if printing:
            print(f"Growing tree...")

        self.length = 1
        self.possible_edges = [list(x) for x in self.adjacency]
        self.degrees        = [len(x)  for x in self.adjacency]
        self.occupied       = [False] * self.area
        self.full_snakes_list = []
        
        for first_head in range(self.area):
            self.first_head = first_head
            self.current_node = self.root.add_child(first_head)
            self.occupied[first_head] = True
            for second_head in self.adjacency[first_head]:
                self.second_head = second_head
                self.current_node.add_child(second_head)
                self.search_branch([second_head])
            self.occupied[first_head] = False
        self.count_and_classify_states()
        if printing:
            self.message_end_of_growth()

    def search_branch(self, stack):
        while stack:
            current_head = stack.pop()
            if self.occupied[current_head]:
                self.unoccupy()
                continue
            self.occupy(current_head)
            stack.append(current_head)
            
            if self.length == self.area:
                self.full_snakes_list.append(self.current_node)
                continue

            if self.safe_winning_snake_is_impossible(current_head):
                continue

            for new_head in self.possible_edges[current_head]:   
                self.current_node.add_child(new_head)       
                stack.append(new_head)

    def occupy(self, current_head):
        possible_edges = self.possible_edges
        degrees = self.degrees       

        # to occupy a vertex, 
        self.length += 1
        prev_head = self.current_node.value
        self.current_node = self.current_node.children[current_head]
        self.occupied[current_head] = True
        # is to make a definite connection between the current and previous heads,
        degrees[current_head] += 1
        degrees[prev_head]    += 1
        # and to cut possible ties between the previous head and other vertices
        lst = possible_edges[prev_head]
        while lst:
            neighbour = lst.pop()
            possible_edges[neighbour].remove(prev_head)
            degrees[neighbour] -= 1
            degrees[prev_head] -= 1

    def unoccupy(self):
        occupied = self.occupied
        possible_edges = self.possible_edges
        degrees = self.degrees

        # to unoccupy a vertex,
        current_head = self.current_node.value

        if self.length != self.area and not self.current_node.children:
            # has no children, so we should delete it
            parent = self.current_node.parent
            self.current_node.parent = None
            del parent.children[current_head]
            self.current_node = parent
        else:
            self.current_node = self.current_node.parent

        prev_head = self.current_node.value
        occupied[current_head] = False
        self.length -= 1

        # is to remove the definite connection between the current and previous heads
        degrees[prev_head]    -= 1
        degrees[current_head] -= 1
        # and to restore possible ties between the previous head and other vertices
        for neighbour in self.adjacency[prev_head]:
            if occupied[neighbour]:
                continue
            possible_edges[neighbour].append(prev_head)
            possible_edges[prev_head].append(neighbour)
            degrees[prev_head] += 1
            degrees[neighbour] += 1

    def safe_winning_snake_is_impossible(self, current_head):
        # check that current_head has somewhere to go
        if not self.possible_edges[current_head]:
            return True
        
        if self.impossible_by_degrees():
            return True
        
        if self.empty_space_is_disconnected(current_head):
            return True

        if self.unsafe_with_2_apples():
            return True
        
        return False
    
    def impossible_by_degrees(self):
        # no HP is possible if there is a vertex of degree 0, or more than 2 of degree 1.
        count_1 = 0
        self.end_point = None
        for v, d in enumerate(self.degrees):
            if d == 0:
                return True
            if d == 1:
                count_1 += 1
                if count_1 == 3:
                    return True
                if v != self.first_head:
                    # any HP must end here!
                    self.end_point = v
        return False
    
    def empty_space_is_disconnected(self, current_head):
        # no HP is possible in that case

        # find some unoccupied cell x
        # we know that the current_head is next to one
        x = self.possible_edges[current_head][0]
        
        # ensure that every unoccupied cell can be reached from x
        stack = [x]
        seen = set([x, current_head])
        while stack:
            y = stack.pop()
            for z in self.possible_edges[y]:
                if z in seen:
                    continue
                stack.append(z)
                seen.add(z)
        return len(seen)-1 != self.area-self.length
    
    def unsafe_with_2_apples(self):

        # a, b, x, y, z represent the 1st, 2nd, 3rd last, 2nd last, last parts of the snake.
        # Under some conditions, we may deduce the safety of the state 
        # based on the connections between these
        # return True if I am sure it is guaranteed to be unsafe, otherwise False
        
        z = self.end_point
        if z is None:
            return False
        # z is a vertex with degree one, we must end there
        
        y, = self.possible_edges[z]
        if self.occupied[y]:
            # win in one
            # y - z
            return False
        
        adjacent_to_first = self.adjacency[self.first_head]
        if z in adjacent_to_first:
            # hamiltonian cycle
            # x - y - z - a - b
            return False
        
        adjacent_to_second = self.adjacency[self.second_head]
        if z in adjacent_to_second:
            # x - y - z - b - a
            return False
        
        for x in self.possible_edges[y]:
            if x == z:
                continue

            if x in adjacent_to_first:
                # cycle and kamikaze
                # x - a - b - ... - ? - z - y
                return False
        
        if y in adjacent_to_first or y in adjacent_to_second:
            # unclear, depends on circumstance and board
            return False
        
        # otherwise, the snake is unsafe
        return True

    def count_and_classify_states(self):
        """Counts the states and classifies the winning snakes."""
        self.num_full_snake = 0
        self.num_hc    = 0
        self.num_theta = 0
        num_nodes = 0
        num_states = 0

        occupied = [False] * self.area
        for first_head in self.root.children.values():
            self.first_head = first_head.value
            occupied[self.first_head] = True
            for second_head in first_head.children.values():
                self.second_head = second_head.value
                occupied[self.second_head] = True
                stack = list(second_head.children.values())
                apple_space = self.area - 2
                while stack:
                    node = stack.pop()
                    num_nodes += 1
                    if occupied[node.value]:
                        occupied[node.value] = False
                        apple_space += 1
                        continue
                    stack.append(node)
                    occupied[node.value] = True
                    apple_space -= 1
                    num_states += apple_space
                    if apple_space == 0:
                        self.classify_full_snake(node)
                    stack.extend(node.children.values())
                occupied[self.second_head] = False
            occupied[self.first_head] = False
        self.num_nodes  = num_nodes
        self.num_states = num_states
        return
    
    def classify_full_snake(self, node):
        """Classifies a full length snake as
        Hamiltonian Cycle or spanning Theta(A-3, 2, 2) subgraph."""
        self.num_full_snake += 1
        z = node.value
        first_adj = self.adjacency[self.first_head]
        if z in first_adj:
            self.num_hc += 1
            return
        y = node.parent.value 
        second_adj = self.adjacency[self.second_head]
        if y in first_adj and z in second_adj:
            self.num_theta += 1

    def message_end_of_growth(self):
        print()
        print(f"Full snakes:        {self.num_full_snake}")
        print(f"Hamiltonian Cycles: {self.num_hc}")
        print(f"Theta subgraphs:    {self.num_theta}")
        print(f"Total nodes:        {self.num_nodes}")
        print(f"Total states:       {self.num_states}")
        delta, total = self.update_time()
        print(f"Time Taken: {delta:.3f}")
        print(f"Total Time: {total:.3f}")
        print()
        return 


class OptimalSnakeTree(SafeWinningSnakeTree):
    """
    Builds the 'optimal play' graph on top of a snake tree.
    """
    
    def __init__(self, adjacency):
        super().__init__(adjacency)

    def build_optimal_graph(self):
        # find the nodes of maximum length
        self.grow_safe_winning_snakes(True)

        # states are prioritised based on score, then apple
        self.stack = [(0, node, None) for node in self.full_snakes_list]

        self.snakes_of_this_length = self.full_snakes_list
        for node in self.full_snakes_list:
            temp_node = node
            while temp_node.parent != self.root:
                temp_node = temp_node.parent
            node.tail = temp_node.value

        self.denominator = 1
        print('len:         layer, length of snake')
        print('t1:          time to build layer')
        print('tot s:       number of snakes in layer')
        print('t2:          time to assign scores in layer')
        print('safe s:      number of safe snakes in layer')
        print('Time:        time since tree created')
        print('tot s:       total snakes in the tree')
        print()
        print(f"{'len'}   {'t1':>8}    {'num s':>10}     {'t2':>8}    {'num safe s':>10}     {'Time':>8}    {'tot s':>10}")
        for self.length in range(self.area-1, 0, -1):          

            self.build_layer()
            delta1, _ = self.update_time()
            num_snakes = len(self.snakes_of_this_length)

            self.assign_scores_to_layer()
            delta2, _ = self.update_time()
            num_clean_snakes = len(self.snakes_of_this_length)

            self.count_nodes()
            _, total = self.update_time()

            print(f"{self.length:>3}   {delta1:>8.3f}    {num_snakes:>10}     {delta2:>8.3f}    {num_clean_snakes:>10}     {total:>8.3f}    {self.num_nodes:>10}")
            
        # now we have the expected values for each spawn location
        score = Fraction(sum(score for score,_,_ in self.stack), self.denominator * self.area)
        
        print()
        print(f"EV  {float(score):.3f}  {score}")
        return score

    def build_layer(self):
        """
        Expands tree to include all snakes of this length 
        which can be reached by 
        removing the head of, or reversing,
        an existing snake
        """
        # for each node of old length, chop off its head
        # then, move the snakes around backwards
        # storing each new snake in the tree
        new_lst = []

        temp_stack = []
        for node in self.snakes_of_this_length:
            new_node = node.parent
            if hasattr(new_node, "score"):
                continue
            new_lst.append(new_node)
            new_node.score = 0
            new_node.apple_to_move = {}
            new_node.past_snakes = []
            new_node.tail = node.tail
            temp_stack.append(new_node)
        
        # split into cases based on length
        # of course, the first is the most expensive

        if self.length > 2:
            while temp_stack:
                node = temp_stack.pop()

                # find past snakes that reach this snake in a single move
                old_head = node.value
                snake_wo_head = self.find_snake(node.parent)
                old_tail = snake_wo_head[0]
                node.tail = old_tail
                body_set = set(snake_wo_head)
                
                for new_tail in self.adjacency[old_tail]:
                    # ensure move is valid
                    if new_tail in body_set:
                        continue

                    new_snake = (new_tail,) + snake_wo_head 
                    new_node = self.add_snake(new_snake)
                    node.past_snakes.append(new_node)

                    # give attributes to this snake if not seen before
                    if hasattr(new_node, "score"):
                        continue
                    new_lst.append(new_node)
                    new_node.score = 0
                    new_node.apple_to_move = {}
                    new_node.past_snakes = []
                    new_node.tail = new_tail
                    temp_stack.append(new_node)
                    
        elif self.length == 2:
            while temp_stack:
                node = temp_stack.pop()

                # find past snakes that reach this snake in a single move
                old_head = node.value
                old_tail = node.parent.value
                for new_tail in self.adjacency[old_tail]:
                    new_snake = (new_tail, old_tail)
                    new_node = self.add_snake(new_snake)
                    node.past_snakes.append(new_node)

                    # give attributes to this snake if not seen before
                    if hasattr(new_node, "score"):
                        continue
                    new_lst.append(new_node)
                    new_node.score = 0
                    new_node.apple_to_move = {}
                    new_node.past_snakes = []
                    new_node.tail = new_tail
                    temp_stack.append(new_node)

        elif self.length == 1:
            while temp_stack:
                node = temp_stack.pop()

                # find past snakes that reach this snake in a single move     
                for new_tail in self.adjacency[node.value]:
                    new_snake = (new_tail,)
                    new_node = self.add_snake(new_snake)
                    node.past_snakes.append(new_node)

                    if hasattr(new_node, "score"):
                        continue
                    new_lst.append(new_node)
                    new_node.score = 0
                    new_node.apple_to_move = {}
                    new_node.past_snakes = []
                    new_node.tail = new_tail
                    temp_stack.append(new_node)
        
        self.snakes_of_this_length = new_lst

    def assign_scores_to_layer(self):
        # assign a score to each snake-apple state
        cost = self.denominator
        stack = self.stack
        while stack:
            score, node, apple = heapq.heappop(stack)
            new_score = score + cost

            if apple is None:
                # this is a snake state
                # chop off head, treat it as apple
                past_node = node.parent 
                new_apple = node.value
                if new_apple in past_node.apple_to_move:
                    continue
                past_node.apple_to_move[new_apple] = node
                past_node.score += new_score
                heapq.heappush(stack, (new_score, past_node, new_apple))
                continue
            
            # this is a snake-apple state
            # move the snake in reverse
            for past_node in node.past_snakes:
                if past_node.tail == apple:
                    continue
                if apple in past_node.apple_to_move:
                    continue
                past_node.apple_to_move[apple] = node
                past_node.score += new_score
                heapq.heappush(stack, (new_score, past_node, apple))
        
        # assign a score to each snake
        stack = []
        clean_lst = []
        num_apples = self.area - self.length
        for node in self.snakes_of_this_length:
            if len(node.apple_to_move) == num_apples:
                heapq.heappush(stack, (node.score, node, None))
                clean_lst.append(node)            
        self.stack = stack
        self.snakes_of_this_length = clean_lst
        self.denominator *= num_apples

    def find_true_size(self):
        tot_nodes = 0
        tot_states = 0
        seen_nodes = set()
        stack = list(self.root.children.values())
        while stack:
            node = stack.pop()
            if node in seen_nodes:
                continue
            seen_nodes.add(node)
            tot_nodes += 1
            if hasattr(node, 'apple_to_move'):
                tot_states += len(node.apple_to_move)
            for child in node.children.values():
                stack.append(child)
        print()
        print(f'Total nodes:    {tot_nodes}')
        print(f'Total states:   {tot_states}')
        print(f'Total wins:     {len(self.full_snakes_list)}')

        seen_nodes  = set()
        seen_states = set()
        seen_wins = set()
        count_nodes = 0
        count_states = 0
        count_wins = 0
        
        # artificial states to kick off
        stack = list(self.root.children.items())
        while stack:
            apple, node = stack.pop()

            if apple == node.value:
                if hasattr(node, 'apple_to_move'):
                    for new_state in node.apple_to_move.items():
                        
                        if new_state not in seen_states:
                            count_states += 1
                            seen_states.add(new_state)
                            stack.append(new_state)
                            _, new_node = new_state
                            if new_node not in seen_nodes:
                                count_nodes += 1
                                seen_nodes.add(new_node)
                else:
                    # this is a win state
                    if node not in seen_wins:
                        count_wins += 1
                        seen_wins.add(node)
            else:
                new_state = (apple, node.apple_to_move[apple])
                if new_state not in seen_states:
                    count_states += 1
                    seen_states.add(new_state)
                    stack.append(new_state)
                    _, new_node = new_state
                    if new_node not in seen_nodes:
                        count_nodes += 1
                        seen_nodes.add(new_node)
        print()
        print(f'Reached nodes:  {count_nodes}')
        print(f'Reached states: {count_states}')
        print(f'Reached wins:   {count_wins}')


"""
Here are some ways to simulate a solver playing a game of snake.
By default, the first should be used.
Each verifies every move made, but has a version that does not, 
for speed testing purposes.
Each can be given a seed to rig the apples.

simulate_rejection_sampling: 
genreates apples uniformly by rejections sampling.
Expected total apple generation time is O(Alog(A)).
Fastest for grid graphs.

simulate_track_empty_space: 
genreates apples uniformly from the empty slots by keeping track of them, 
Expected total apple generation time is O(|moves|).
"""
from random import choice
from random import seed as rand_set_seed

def simulate_rejection_sampling(adjacency, solver, seed=None): 
    if seed != None:
        rand_set_seed(seed)   
    area = len(adjacency)
    vertices = list(range(area))
    moves_per_apple = [0] * (area-1)
    occupied = [False] * area
    next_tail = [None] * area
    start = choice(vertices)
    occupied[start] = True
    head = start
    tail = head
    solver.start_new_game(start)
    apple = head
    for apple_num in range(area-1):
        while occupied[apple]:
            apple = choice(vertices)
        move_counter = 0
        for new_head in solver.find_path(apple):
            move_counter += 1
            if new_head not in adjacency[head]:
                return None
            if new_head == apple:
                occupied[apple] = True
                next_tail[head] = apple
                head = apple
                break
            occupied[tail] = False
            if occupied[new_head]:
                return None
            occupied[new_head] = True
            next_tail[head] = new_head
            head = new_head
            tail = next_tail[tail]
        moves_per_apple[apple_num] = move_counter
    return moves_per_apple

def simulate_track_empty_space(adjacency, solver, seed=None): 
    if seed != None:
        rand_set_seed(seed)   
    area = len(adjacency)
    occupied = [False] * area
    where_head_went_from_here = [None] * area
    
    empty_vertices = list(range(area)) 
    empty_indices = list(range(area))  

    start = choice(empty_vertices)
    solver.start_new_game(start)
    occupied[start] = True
    head = start
    tail = start

    temp = empty_vertices[-1]
    empty_vertices[start] = temp
    empty_indices[temp] = start
    empty_vertices.pop()

    moves_per_apple = [0] * (area-1)
    for apple_num in range(area-1):
        apple = choice(empty_vertices)
        move_counter = 0
        for new_head in solver.find_path(apple):
            move_counter += 1
            if new_head not in adjacency[head]:
                return None
            if new_head == apple:
                i = empty_indices[apple]
                temp = empty_vertices[-1]
                empty_vertices[i] = temp
                empty_indices[temp] = i
                empty_vertices.pop()

                occupied[apple] = True
                where_head_went_from_here[head] = apple
                head = apple
                break
            occupied[tail] = False
            if occupied[new_head]:
                return None
            i = empty_indices[new_head]
            empty_vertices[i] = tail
            empty_indices[tail] = i

            occupied[new_head] = True
            where_head_went_from_here[head] = new_head
            head = new_head
            tail = where_head_went_from_here[tail]

        moves_per_apple[apple_num] = move_counter
    return moves_per_apple

def run_multiple_games(adjacency, solver, N, tester = simulate_rejection_sampling):
    """
    Collects moves-per-apple and total moves over N games
    """
    total_moves = []
    total_moves_per_apple = [0] * (len(adjacency)-1)
    num_fails = 0
    for game in range(N):
        moves_per_apple = tester(adjacency, solver)
        if moves_per_apple is None:
            num_fails += 1
            print('Failure: ' + solver.name)
            continue
        total_moves.append( sum(moves_per_apple) )
        for apple, moves in enumerate(moves_per_apple):
            total_moves_per_apple[apple] += moves
    num_passes = N - num_fails
    avg_moves_per_apple = [x/num_passes for x in total_moves_per_apple]  
    return total_moves, avg_moves_per_apple, num_fails
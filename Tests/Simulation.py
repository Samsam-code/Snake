from random import choice
from random import seed as rand_set_seed


def simulate_rejection_sampling(adjacency, solver, seed=None): 
    if seed is not None:
        rand_set_seed(seed)   
    area = len(adjacency)
    vertices = list(range(area))
    moves_per_apple = [0] * (area-1)
    carved_path = [None] * area

    start = choice(vertices)
    head = start
    tail = head
    apple = head

    apples_eaten = 0
    moves_this_apple = 0
    while carved_path[apple] is not None or apple == head:
        apple = choice(vertices)
    solver.apple = apple
    
    for new_head in solver.yield_moves_to_simulator(start):
        if new_head not in adjacency[head]:
            return None
        moves_this_apple += 1
        carved_path[head] = new_head
        head = new_head

        if new_head == apple:
            moves_per_apple[apples_eaten] = moves_this_apple
            apples_eaten += 1
            if apples_eaten == area-1:
                return moves_per_apple
            moves_this_apple = 0
            while carved_path[apple] is not None or apple == head:
                apple = choice(vertices)
            solver.apple = apple
            continue

        new_tail = carved_path[tail]
        carved_path[tail] = None
        tail = new_tail
        if carved_path[new_head] is not None:
            return None
        

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
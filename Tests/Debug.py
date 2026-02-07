import time
from random import choice
from random import seed as rand_set_seed
from GridsAndGraphs.Adjacencies import find_adjacency_grid


def simulate_debug_rejection_sampling(adjacency, solver, seed=None): 
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
            print('ERROR: non-adjacent move!')
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
            print('ERROR: collision with body!')
            return None

def animate_failures(m, n, N, solver, animator, tester = simulate_debug_rejection_sampling):
    adjacency = find_adjacency_grid(m, n)
    total_moves = [0] * N
    total_moves_per_apple = [0] * (len(adjacency)-1)
    failed_seeds = []
    num_fails = 0
    for game in range(N):
        seed = time.time_ns()
        print(seed)
        moves_per_apple = tester(adjacency, solver, seed)
        if moves_per_apple is None:
            num_fails += 1
            failed_seeds.append(seed)
            print('Failure: ' + solver.name + f' {seed}')
            while True:
                answer = input("Do you want to run the animation? (y/n): ").strip().lower()
                if answer in ("y", "yes"):
                    animator.animate_single_game(seed)
                elif answer in ("n", "no"):
                    break
                else:
                    print("Please enter 'y' or 'n'.")
                    continue
        total_moves[game] = sum(moves_per_apple)
        for apple, moves in enumerate(moves_per_apple):
            total_moves_per_apple[apple] += moves
        print(game, 'Success')
    num_passes = N - num_fails
    avg_moves_per_apple = [x/num_passes for x in total_moves_per_apple]  
    return total_moves, avg_moves_per_apple, num_fails
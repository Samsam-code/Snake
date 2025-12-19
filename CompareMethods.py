from random import choice
from collections import deque
import time
import statistics
import matplotlib.pyplot as plt
from GridSpecificTools.GridGraphAndSymmetries import find_grid_adjacency, find_geometric_lower_bound
import numpy as np
from ExactValues.Loop import find_Loop_PDF
        


def run_single_game(adjacency, solver):    
    area = len(adjacency)

    # keep track of occupied, empty vertices
    occupied = [False] * area
    empty_vertices = list(range(area))  # list of empty vertices
    empty_indices = list(range(area))   # index of empty vertex within that list

    # choose starting location, pass to solver
    start = choice(empty_vertices)
    solver.start_new_game(start)
    
    occupied[start] = True
    snake = deque([start])
    head = start
    
    # update empty space
    i = empty_indices[start]
    temp = empty_vertices[-1]
    empty_vertices[i] = temp
    empty_indices[temp] = i
    empty_vertices.pop()

    score_per_apple = [0] * (area-1)
    for apple_num in range(area-1):
        # generate random apple, ask solver for path to apple
        apple = choice(empty_vertices)
        path = solver.find_path(apple)

        for new_head in path[:-1]:
            # move tail, check legality, move head
            old_tail = snake.popleft()
            occupied[old_tail] = False

            if new_head not in adjacency[head]:
                print('ERROR: non-adjacent move!')
                return None
            if occupied[new_head]:
                print('ERROR: collision with body!')
                return None
            if new_head == apple:
                print('ERROR: collision with apple!')
                return None
            
            occupied[new_head] = True
            snake.append(new_head)
            head = new_head

            # replace new_head by old_tail in empty vertices list
            # unless they are the same (then neither are in that list)
            if new_head == old_tail:
                continue
            i = empty_indices[new_head]
            empty_vertices[i] = old_tail
            empty_indices[old_tail] = i
            
        # check and execute final move
        if path[-1] != apple:
            print('ERROR: missed apple!')
            return None
        if apple not in adjacency[head]:
            print('ERROR: non-adjacent move!')
            return None

        occupied[apple] = True
        snake.append(apple) 
        head = apple

        # remove apple from list of empty vertices
        i = empty_indices[apple]
        temp = empty_vertices[-1]
        empty_vertices[i] = temp
        empty_indices[temp] = i
        empty_vertices.pop()

        score_per_apple[apple_num] = len(path)
    return score_per_apple


def run_multiple_games(adjacency, solver, N):
    """
    Collects score-per-apple and total score over N
    """
    scores = [0] * N
    total_score_per_apple = [0] * (len(adjacency)-1)
    for game in range(N):
        score_per_apple = run_single_game(adjacency, solver)
        if score_per_apple is None:
            return 
        scores[game] = sum(score_per_apple)
        for apple, score in enumerate(score_per_apple):
            total_score_per_apple[apple] += score
    avg_score_per_apple = [x/N for x in total_score_per_apple]  
    return scores, avg_score_per_apple


def compare_methods_on_grid(m, n, N, solvers, against_exact_Loop_PDF):

    adjacency = find_grid_adjacency(m, n)
    area = m * n

    fig1, ax1 = plt.subplots(1)  
    ax1.set_title(f'Score Distribution over {N} tests on {m}x{n} grid')
    ax1.set_xlabel('Score')
    ax1.set_ylabel('Probability')

    fig2, ax2 = plt.subplots(1)
    ax2.set_title(f'Score-per-apple over {N} tests on {m}x{n} grid')
    ax2.set_xlabel('apple')
    ax2.set_ylabel('average moves taken')
    apple_axis = list(range(area-1))

    last_time = time.time()
    print(f"{'Method':<20} {'Mean Score':>12} {'Std Dev':>12} {'Time':>10}")
    

    # if not odd-by-odd grid, plot some Loop expectation data
    if area % 2 == 0:
        Loop_score_per_apple = [(area-a)/2 for a in apple_axis]  
        Loop_mean = (area-1)*(area+2)/4
        Loop_std  = np.sqrt((area-1)*(2*area*area-area-6)/72)
        max_score = int(Loop_mean + 3 * Loop_std) 
        ax1.set_xlim(0, max_score)
        score_axis = list(range(max_score))

        print(f"{'Loop Expectation':<20} "
        f"{Loop_mean:>12.3f} "
        f"{Loop_std:>12.3f} "
        f"{'-':>10}")

        if against_exact_Loop_PDF:
            Loop_PDF = find_Loop_PDF(area)
        else:
            a = 1/(Loop_std*np.sqrt(2*np.pi))
            b = -1/(2*Loop_std*Loop_std)
            def gaussian(x):
                return a*np.exp(b*(x-Loop_mean)**2)
            Loop_PDF = [gaussian(x) for x in score_axis]

        delta_time = time.time()-last_time
        last_time += delta_time        
        ax1.plot(Loop_PDF, color='black', linestyle='-', linewidth=2, label='Loop Expectation')
        ax2.plot(apple_axis, Loop_score_per_apple, 
                color='black', linestyle='-', linewidth=2, label='Loop Expectation')
    

    scotts_constant = 3.5 * N**(-1/3)   # best bin width according to Scott's rule
    for solver in solvers:
        scores, avg_score_per_apple = run_multiple_games(adjacency, solver, N)
        mean = statistics.mean(scores)
        std  = statistics.stdev(scores)
        delta_time = time.time()-last_time
        last_time += delta_time
        print(f"{solver.name:<20} "
            f"{mean:>12.3f} "
            f"{std:>12.3f} "
            f"{delta_time:>10.3f}")

        bin_width = max(int(std * scotts_constant ), 1)
        min_val = (min(scores)//bin_width) * bin_width
        max_val = (max(scores)//bin_width) * bin_width
        bins = np.arange(min_val - 0.5, max_val + 1.5, bin_width)
        ax1.hist(scores, bins=bins, density=True, alpha=0.5, label = solver.name)
        ax2.plot(apple_axis, avg_score_per_apple, linewidth=2, label = solver.name)

    ax1.legend()
    ax2.legend()
    plt.show() 


if __name__ == "__main__":
    from Methods.Loop import GridSolverLoop    
    m = 16
    n = 16
    N = 1_000
    solvers = [GridSolverLoop(m, n)]
    compare_methods_on_grid(m, n, N, solvers, False)
"""
Modified versions of the tester and comparison functions
for the Dinosaur minigame of The Farmer Was Replaced.
Takes in to account non-uniformity of apple generation
and estimates movement ticks.
"""
from random import choice
from random import seed as rand_set_seed
import time
import statistics
import matplotlib.pyplot as plt
import numpy as np
from GridsAndGraphs.Adjacencies import find_adjacency_grid
from Tests.Simulation import run_multiple_games

def find_ticks_per_apple(area):
    ticks_per_apple = [None] * (area-1)
    ticks = 400
    for i in range(area-1):
        to_remove = ticks * 0.03 // 1
        if to_remove == 0:
            break
        ticks -= to_remove
        ticks_per_apple[i] = ticks
    for j in range(i, area-1):
        ticks_per_apple[j] = ticks
    return ticks_per_apple

def simulate_tfwr_rejection_sampling(adjacency, solver, seed=None): 
    if seed != None:
        rand_set_seed(seed)   
    area = len(adjacency)
    vertices = list(range(area))
    score_per_apple = [0] * (area-1)
    occupied = [False] * area
    next_tail = [None] * area
    start = choice(vertices)
    occupied[start] = True
    head = start
    tail = head
    move_generator = solver.yield_moves_to_simulator(start)
    next_apple = choice(vertices)
    while next_apple == start:
        next_apple = choice(vertices)
    for apple_num in range(area-1):
        apple = next_apple
        if apple_num < area-2:
            next_apple = choice(vertices)
            while next_apple == apple or occupied[next_apple]:
                next_apple = choice(vertices)
        move_counter = 0
        solver.apple = apple
        while True:
            new_head = next(move_generator)
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

            if head == next_apple and apple_num != area-2:
                next_apple = choice(vertices)
                while occupied[next_apple] or next_apple == apple:
                    next_apple = choice(vertices)
                solver.next_apple = next_apple
        score_per_apple[apple_num] = move_counter
    return score_per_apple

def compare_methods_tfrw(m, n, N, solvers, colours = None):
    """
    Runs N games on an m x n grid for each solver in solvers,
    with apple generation as in TFWR,
    plots score distributions, mean moves per apple,
    and mean movement ticks per apple.
    """
    print(f"Comparing methods on {m}x{n} grid over {N} games:")
    print(f"{'Method':<20}{'Mean':>12}{'Std Dev':>10}{'Time':>8}{'Fails':>8}{'Ticks':>12}")
    
    area = m * n
    apple_axis = list(range(area-1)) # number of apples eaten, length-1
    ticks_per_apple = find_ticks_per_apple(area)

    fig1, ax1 = plt.subplots(1)  
    ax1.set_title(f'Score Distribution over {N} tests on {m}x{n} grid')
    ax1.set_xlabel('Score')
    ax1.set_ylabel('Probability')

    fig2, ax2 = plt.subplots(1)
    ax2.set_title(f'Mean moves per apple over {N} tests on {m}x{n} grid')
    ax2.set_xlabel('apple')
    ax2.set_ylabel('mean moves taken')

    fig3, ax3 = plt.subplots(1)
    ax3.set_title(f'Mean movement ticks per apple over {N} tests on {m}x{n} grid')
    ax3.set_xlabel('apple')
    ax3.set_ylabel('average movement ticks')

    print(f"{'Arch TFWR Dino WR':<20}"
        f"{'-':>12}"
        f"{'-':>10}"
        f"{'-':>8}"
        f"{'-':>8}"
        f"{3250000:>12}"
    )
    
    if colours == None or len(colours) < len(solvers):
        cmap = plt.get_cmap("tab10")   # try "tab20" if many solvers
        colours = [cmap(i) for i in range(len(solvers))]

    adjacency = find_adjacency_grid(m, n)
    scotts_constant = 3.5 * N**(-1/3)   
    last_time = time.time()
    for index, solver in enumerate(solvers):
        scores, avg_score_per_apple, num_fails = run_multiple_games(adjacency, solver, N, 
                                                        tester = simulate_tfwr_rejection_sampling)
        mean = statistics.mean(scores)
        std  = statistics.stdev(scores)

        bin_width = max(int(std * scotts_constant ), 1) # best bin width according to Scott's rule
        min_val = (min(scores)//bin_width) * bin_width
        max_val = (max(scores)//bin_width) * bin_width
        bins = np.arange(min_val - 0.5, max_val + 1.5, bin_width)
        ax1.hist(scores, bins=bins, density=True, color=colours[index], alpha=0.5, label = solver.name)
        ax2.plot(apple_axis, avg_score_per_apple, color=colours[index], linewidth=2, label = solver.name)

        avg_ticks_per_apple = [weight* score for weight, score in zip(ticks_per_apple, avg_score_per_apple)]
        total_ticks = int(sum(avg_ticks_per_apple))
        ax3.plot(apple_axis, avg_ticks_per_apple, linewidth=2, label = solver.name)

        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time 
        
        print(f"{solver.name:<20}"
            f"{mean:>12.3f}"
            f"{std:>10.3f}"
            f"{delta_time:>8.3f}"
            f"{num_fails:>8}"
            f"{total_ticks:>12}"
        )

    ax1.legend()
    ax2.legend()
    plt.show() 
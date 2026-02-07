import time
import statistics
import matplotlib.pyplot as plt
import numpy as np
from GridsAndGraphs.Adjacencies import find_adjacency_grid
from Tests.Simulation import run_multiple_games        

def compare_methods(m, n, N, solvers, plot_estimates = False, colours = None):
    """
    Runs N games on an m x n grid for each solver in solvers,
    plots score distributions and mean moves per apple.
    """
    print(f"Comparing methods on {m}x{n} grid over {N} games:")
    print(f"{'Method':<20}{'Mean':>12}{'Std Dev':>10}{'Time':>8}{'Fails':>8}{'Estimate':>12}")
    
    area = m * n
    apple_axis = list(range(area-1)) # number of apples eaten, length-1

    fig1, ax1 = plt.subplots(1)  
    ax1.set_title(f'Score Distribution over {N} tests on {m}x{n} grid')
    ax1.set_xlabel('Score')
    ax1.set_ylabel('Probability')

    fig2, ax2 = plt.subplots(1)
    ax2.set_title(f'Mean moves per apple over {N} tests on {m}x{n} grid')
    ax2.set_xlabel('apples easten')
    ax2.set_ylabel('mean moves to next apple')
    
    if colours == None or len(colours) < len(solvers):
        cmap = plt.get_cmap("tab10")   # try "tab20" if many solvers
        colours = [cmap(i) for i in range(len(solvers))]
    
    estimate_totals = ['-'] * len(solvers)
    if plot_estimates:
        for index, solver in enumerate(solvers):
            if not hasattr(solver, "estimate_moves_per_apple"):
                continue
            estimate_mpa = solver.estimate_moves_per_apple()
            estimate_total = sum(estimate_mpa)
            ax1.axvline(estimate_total, color=colours[index], linestyle='--')
            ax2.plot(apple_axis, estimate_mpa, color=colours[index], linestyle='--')
            estimate_totals[index] = int(estimate_total)
    
    adjacency = find_adjacency_grid(m, n)
    scotts_constant = 3.5 * N**(-1/3)   
    last_time = time.time()
    for index, solver in enumerate(solvers):
        scores, avg_score_per_apple, num_fails = run_multiple_games(adjacency, solver, N)
        mean = statistics.mean(scores)
        std  = statistics.stdev(scores)

        bin_width = max(int(std * scotts_constant ), 1) # best bin width according to Scott's rule
        min_val = (min(scores)//bin_width) * bin_width
        max_val = (max(scores)//bin_width) * bin_width
        bins = np.arange(min_val - 0.5, max_val + 1.5, bin_width)
        ax1.hist(scores, bins=bins, density=True, color=colours[index], alpha=0.5, label = solver.name)
        ax2.plot(apple_axis, avg_score_per_apple, color=colours[index], linewidth=2, label = solver.name)

        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time 
        
        print(f"{solver.name:<20}"
            f"{mean:>12.3f}"
            f"{std:>10.3f}"
            f"{delta_time:>8.3f}"
            f"{num_fails:>8}"
            f"{estimate_totals[index]:>12}"
        )

    ax1.legend()
    ax2.legend()
    plt.show() 
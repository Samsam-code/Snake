from Tests.RunGames import compare_methods_on_grid

from GridSpecificTools.DiveCycle import double_comb_cycle, zip_cycle

# import methods you want
from Methods.Loop import GridSolver_Loop
from Methods.LoopAndMaxSkip import GridSolver_LoopAndMaxSkip
from Methods.LoopAndGreedySkip import GridSolver_LoopAndGreedySkip
from Methods.Dive import GridSolver_Dive
from Methods.FastForward import Optimizer_FastForward
from Methods.AsymDive import GridSolver_AsymDive

# choose grid size, m <= n
m = 16
n = 16

# choose number of games to run per method
N = 2_500

# initialise solvers
solvers = [
    #GridSolver_Loop(m, n),
    #Optimizer_FastForward(GridSolver_Loop, m, n),
    #GridSolver_LoopAndMaxSkip(m, n, find_HC=double_comb_cycle),
    GridSolver_LoopAndGreedySkip(m, n, find_HC=double_comb_cycle),
    #GridSolver_Dive(m, n),
    Optimizer_FastForward(GridSolver_Dive, m, n),
    GridSolver_AsymDive(m, n),
    Optimizer_FastForward(GridSolver_AsymDive, m, n),
]

against_exact_Loop_PDF = False      # set to True to compare against exact Loop PDF, on small grids only!
compare_methods_on_grid(m, n, N, solvers, against_exact_Loop_PDF)
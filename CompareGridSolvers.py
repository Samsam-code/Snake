# import test to run
from Tests.Comparison import compare_methods
#from Tests.ComparisonTFWR  import compare_methods_tfrw

# import methods to test
from GridSolvers.Loop import GridSolver_Loop
from GridSolvers.LoopAndSkip import GridSolver_LoopAndGreedySkip
from GridSolvers.Dive import GridSolver_Dive
from GridSolvers.AsymDive import GridSolver_AsymDive
from GridSolvers.FastForward import Optimizer_FastForward

# choose grid size, 2 <= m <= n
m = 16
n = 16

# choose number of games to run per solver
N = 1000

# initialise solvers
solvers = [
    GridSolver_Loop(m, n),
    GridSolver_LoopAndGreedySkip(m, n),
    Optimizer_FastForward(GridSolver_Loop, m, n),
    GridSolver_Dive(m, n),
    GridSolver_AsymDive(m, n),
]

compare_methods(m, n, N, solvers, plot_estimates=True)
#compare_methods_tfrw(m, n, N, solvers)
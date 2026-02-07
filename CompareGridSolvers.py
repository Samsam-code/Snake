# import test to run
from Tests.Comparison import compare_methods
from Tests.ComparisonTFWR  import compare_methods_tfrw

# import methods to test

from GridSolvers.Loop import GridSolver_Loop
from GridSolvers.LoopAndSkip import GridSolver_LoopAndSkip
from GridSolvers.AsymDive import GridSolver_AsymDive
from GridSolvers.DronesRules import GridSolver_DronesRules_TransitionHC
from GridSolvers.SafePath import  GridSolver_SPF_AOW_TransitionHC


# choose grid size, 2 <= m <= n
m = 32
n = 32

# choose number of games to run per solver
N = 1000

# initialise solvers
solvers = [
    GridSolver_Loop(m, n),
    GridSolver_LoopAndSkip(m, n),
    GridSolver_AsymDive(m, n),
    GridSolver_DronesRules_TransitionHC(m, n),
    GridSolver_SPF_AOW_TransitionHC(m, n)
]

compare_methods(m, n, N, solvers, plot_estimates=False)
#compare_methods_tfrw(m, n, N, solvers)
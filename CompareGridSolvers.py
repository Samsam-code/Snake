from Tests.RunGames import compare_methods_on_grid

# import methods you want
from Methods.Loop import GridSolver_Loop
from Methods.LoopAndSkip import GridSolver_LoopAndSkip

# choose grid size, m <= n
m = 16
n = 16

# choose number of games to run per method
N = 1_000

# initialise solvers
solver1 = GridSolver_Loop(m, n)
solver2 = GridSolver_LoopAndSkip(m, n)

# run comparison
solvers = [solver1, solver2]
against_exact_Loop_PDF = False      # set to True to compare against exact Loop PDF, on small grids only!
compare_methods_on_grid(m, n, N, solvers, against_exact_Loop_PDF)
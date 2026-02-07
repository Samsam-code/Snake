"""
Runs a large number of games, animates the games where the solver fails.
This should make algorithm development much faster:)
"""

# import test to run
from Tests.Animation import GridAnimator
from Tests.Debug import animate_failures

# import method to test
from GridSolvers.DronesRules import GridSolver_DronesRules

# choose grid size, m <= n
m = 16
n = 16

# choose number of games
N = 1000

# initialise solver
solver = GridSolver_DronesRules(m, n)

# run test
animator = GridAnimator(m, n, solver)
animate_failures(m, n, N, solver, animator)
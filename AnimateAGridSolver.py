from Tests.Animation import GridAnimator

from GridSpecificTools.DiveCycle import double_comb_cycle, zip_cycle
# import method you want
from Methods.FastForward import Optimizer_FastForward
from Methods.Loop import GridSolver_Loop
from Methods.LoopAndMaxSkip import GridSolver_LoopAndMaxSkip
from Methods.LoopAndGreedySkip import GridSolver_LoopAndGreedySkip
from Methods.Dive import GridSolver_Dive
from Methods.AsymDive import GridSolver_AsymDive

# choose grid size, m <= n
m = 8
n = 8

# initialise solvers
solver = GridSolver_AsymDive(m, n)

# run comparison
animator = GridAnimator(m, n, solver)
scores = animator.animate_many_games()
print(scores)
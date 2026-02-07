# import test to run
from Tests.Animation import GridAnimator

# import method to test
from GridSolvers.Loop import GridSolver_Loop
from GridSolvers.LoopAndSkip import GridSolver_LoopAndSkip
from GridSolvers.DronesRules import GridSolver_DronesRules


# choose grid size, m <= n
m = 16
n = 16

# initialise solvers
from GridSolvers.SafePath import  GridSolver_SPF_AOW_BFS

solver = GridSolver_SPF_AOW_BFS(m, n)

# run test
animator = GridAnimator(m, n, solver, FPS=1)

scores = animator.animate_many_games()
print(scores)
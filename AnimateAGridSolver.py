# import test to run
from Tests.Animation import GridAnimator

# import method to test
from GridSolvers.Loop import GridSolver_Loop
from GridSolvers.LoopAndSkip import GridSolver_LoopAndSkip
from GridSolvers.DronesRules import GridSolver_DronesRules, GridSolver_DronesRules_TransitionHC
from GridSolvers.SafePath import  GridSolver_SPF_AOW_TransitionHC



# choose grid size, m <= n
m = 32
n = 32

# initialise solvers
solver = GridSolver_DronesRules_TransitionHC(m, n)

# run test
animator = GridAnimator(m, n, solver, FPS=1)

scores = animator.animate_many_games()
print(scores)
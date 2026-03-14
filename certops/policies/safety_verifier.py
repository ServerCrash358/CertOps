from z3 import *

def verify_scaling(pods, max_pods):

    solver = Solver()

    pods_var = Int("pods")

    solver.add(pods_var == pods)
    solver.add(pods_var <= max_pods)

    if solver.check() == sat:
        return True
    else:
        return False
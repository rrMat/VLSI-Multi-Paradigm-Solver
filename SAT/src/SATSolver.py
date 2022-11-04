from z3 import *

class SATSolver:

    def __init__(self, timeout = None):
        self.solver = Solver()
        if timeout != None:
            self.solver.set(timeout= timeout * 1000)

    def add_constraint(self, constraint):
        self.solver.add(constraint)

    def solve(self):
        return self.solver.check()

    def get_model(self):
        return self.solver.model()
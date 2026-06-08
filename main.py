"""
Esse programa simplesmente demonstra o uso do OptFrame para resolver o problema 
da mochila (Knapsack Problem - KP) usando Simulated Annealing (SA).
"""


import optframe
from optframe.components import Move

"""
Representação de uma solução do problema da mochila
"""
class SolutionKP(object):
    def __init__(self):
        self.n : int = 0 # Number of items in solution
        self.bag : list[int] = [] # selected items in solution

    def __str__(self):
        return f"SolutionKP(n={self.n}, bag={self.bag})"


"""
Representação do problema da mochila
"""
class ExampleKP(object):
    def __init__(self):
        self.engine = optframe.Engine()
        self.n : int = 0 # Number of items
        self.w : list[int] = [] # Weights of items
        self.p : list[int] = [] # Profits of items
        self.Q : float = 0.0 # Capacity of the knapsack


    """
        Load problem data from a text file
    """
    def load(self, filename: str):
        with open(filename, 'r') as f:
            lines = f.readlines()
            self.n = int(lines[0])
            self.Q = int(lines[1])
            p_lines = lines[2].split()
            self.p = [int(x) for x in p_lines]
            w_lines = lines[3].split()
            self.w = [int(x) for x in w_lines]

    def __str__(self):
        return f"ExampleKP(n={self.n}, Q={self.Q}, p={self.p}, w={self.w})"

    """
        Generate a random solution for the problem
    """
    @staticmethod
    def generateSolution(problem: 'ExampleKP') -> SolutionKP:
        import random
        sol = SolutionKP()
        sol.n = problem.n
        sol.bag = [random.randint(0, 1) for _ in range (sol.n)]
        return sol

    """
        Evaluate the solution (to be maximized)
    """
    @staticmethod
    def maximize(pKP: 'ExampleKP', sol: SolutionKP) -> float:
        import numpy as np
        wsum = np.dot(sol.bag, pKP.w)
        if wsum > pKP.Q:
            return -1000.0 * (wsum - pKP.Q)  # Penalty for exceeding capacity

        return np.dot(sol.bag, pKP.p)


"""
A move that flips the k-th bit of the solution
"""
class MoveBitFlip(Move):
    def __init__(self, _k : int):
        self.k = _k

    def apply(self, problemCtx: ExampleKP, sol: SolutionKP) -> 'MoveBitFlip':
        sol.bag[self.k] = 1 - sol.bag[self.k]  # Flip the k-th bit
        return MoveBitFlip(self.k)

    def canBeApplied(self, problemCtx: ExampleKP, sol: SolutionKP) -> bool:
        return True

    def eq(self, problemCtx: ExampleKP, m2: 'MoveBitFlip') -> bool:
        return super().eq(problemCtx, m2)

class NSBitFlip(object):
    @staticmethod
    def randomMove(pKP: ExampleKP, sol: SolutionKP) -> MoveBitFlip:
        import random
        k = random.randint(0, pKP.n - 1)
        return MoveBitFlip(k)




pKP = ExampleKP()
pKP.load("./pyoptframe-dev/demo/02_QuickstartKP_SA/knapsack-example.txt")

#pKP.n = 5
#pKP.w = [1, 2, 3, 7, 8]
#pKP.p = [1, 1, 1, 5, 5]
#pKP.Q = 10.0

pKP.engine.setup(pKP)
ev_idx = 0
c_idx = 0
is_idx = 0

# Register NS Class

pKP.engine.add_ns_class(pKP, NSBitFlip)
ns_idx = 0


fev = pKP.engine.get_evaluator(ev_idx)
pKP.engine.print_component(fev)

fc = pKP.engine.get_constructive(c_idx)
pKP.engine.print_component(fc)

solxx = pKP.engine.fconstructive_gensolution(fc)
print("Constructive solution:", solxx)


z1 = pKP.engine.fevaluator_evaluate(fev, False, solxx)
print("Objective value of constructive solution:", z1)


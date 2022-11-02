from itertools import combinations
from z3 import *
import utils 
import math
import time
from tqdm import tqdm
import numpy as np

def all_true(bool_vars):
    return And(bool_vars)

def at_least_one(bool_vars):
    return Or(bool_vars)

def at_most_one(bool_vars):
    return [Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)]

def exactly_one(bool_vars):
    return at_most_one(bool_vars) + [at_least_one(bool_vars)]

def bool_greater_eq(x, y):
    return Or(x, Not(y))
    
def z3_less_eq(x, y):
    return And(
            [bool_greater_eq(x[0], y[0])] +
            [
                Implies(
                    And([x[j] == y[j] for j in range(i)]),
                    bool_greater_eq(x[i], y[i])
                )
                for i in range(1, len(x))
            ]
    )

def z3_lex_less_eq(x, y, n):
    return And([z3_less_eq(x[0], y[0])] + [Implies(
                                                And([And([x[j][k] == y[j][k] for k in range(n)]) for j in range(i)]),
                                                z3_less_eq(x[i], y[i])
                                            ) for i in range(1, len(x))]
                )
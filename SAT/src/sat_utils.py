from itertools import combinations
from z3 import *
import math
import time
from tqdm import tqdm
import numpy as np
import random 


# NP
def at_least_one_np(bool_vars):
    return Or(bool_vars)

def at_most_one_np(bool_vars):
    tmp = [Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)]
    return And(tmp)

def exactly_one_np(bool_vars):
    return And(at_most_one_np(bool_vars), at_least_one_np(bool_vars))

# HE
def at_least_one_he(bool_vars):
    return at_least_one_np(bool_vars)

def at_most_one_he(bool_vars):
    name = ''.join(random.choice(v) for i in range(10))
    if len(bool_vars) <= 4:
        return And(at_most_one_np(bool_vars))
    y = Bool(f"y_{name}")
    return And(And(at_most_one_np(bool_vars[:3] + [y])), And(at_most_one_he(bool_vars[3:] + [Not(y)])))

def exactly_one_he(bool_vars):
    return And(at_most_one_he(bool_vars), at_least_one_he(bool_vars))


at_least_one = {
    'np': at_least_one_np,
    'he': at_least_one_he
}

at_most_one = {
    'np': at_most_one_np,
    'he': at_most_one_he
}

exactly_one = {
    'np': exactly_one_np,
    'he': exactly_one_he
}

def all_true(bool_vars):
    return And(bool_vars)

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
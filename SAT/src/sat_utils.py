from itertools import combinations
from z3 import *
import math
import time
from tqdm import tqdm
import numpy as np
import random 


# Naive Paiwise
def at_least_one_np(bool_vars):
    return Or(bool_vars)

def at_most_one_np(bool_vars):
    tmp = [Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)]
    return And(tmp)

def exactly_one_np(bool_vars):
    return And(at_most_one_np(bool_vars), at_least_one_np(bool_vars))

# Sequential
def at_least_one_seq(bool_vars):
    return at_least_one_np(bool_vars)

def at_most_one_seq(bool_vars, name):
    constraints = []
    n = len(bool_vars)
    s = [Bool(f"s_{name}_{i}") for i in range(n - 1)]
    constraints.append(Or(Not(bool_vars[0]), s[0]))
    constraints.append(Or(Not(bool_vars[n-1]), Not(s[n-2])))
    for i in range(1, n - 1):
        constraints.append(Or(Not(bool_vars[i]), s[i]))
        constraints.append(Or(Not(bool_vars[i]), Not(s[i-1])))
        constraints.append(Or(Not(s[i-1]), s[i]))
    return And(constraints)

def exactly_one_seq(bool_vars, name):
    return And(at_least_one_seq(bool_vars), at_most_one_seq(bool_vars, name))

# Bitwise
def toBinary(num, length = None):
    num_bin = bin(num).split("b")[-1]
    if length:
        return "0"*(length - len(num_bin)) + num_bin
    return num_bin
    
def at_least_one_bw(bool_vars):
    return at_least_one_np(bool_vars)

def at_most_one_bw(bool_vars, name):
    constraints = []
    n = len(bool_vars)
    m = math.ceil(math.log2(n))
    r = [Bool(f"r_{name}_{i}") for i in range(m)]
    binaries = [toBinary(i, m) for i in range(n)]
    for i in range(n):
        for j in range(m):
            phi = Not(r[j])
            if binaries[i][j] == "1":
                phi = r[j]
            constraints.append(Or(Not(bool_vars[i]), phi))        
    return And(constraints)

def exactly_one_bw(bool_vars, name):
    return And(at_least_one_bw(bool_vars), at_most_one_bw(bool_vars, name)) 

# Heule
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
    'seq': at_least_one_seq,
    'bw': at_least_one_bw,
    'he': at_least_one_he,
}

at_most_one = {
    'np': at_most_one_np,
    'seq': at_most_one_seq,
    'bw': at_most_one_bw,
    'he': at_most_one_he
}

exactly_one = {
    'np': exactly_one_np,
    'seq': exactly_one_seq,
    'bw': exactly_one_bw,
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
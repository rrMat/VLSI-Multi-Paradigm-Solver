from itertools import combinations
from z3 import *
import math
import time
from tqdm import tqdm
import numpy as np
import random 
import os
from random import randint
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.legend_handler import HandlerTuple
from matplotlib.image import imread
import pandas as pd
import numpy as np



def all_true(bool_vars):
    return And(bool_vars)

def all_false(bool_vars):
    return And([Not(var) for var in bool_vars])


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

def at_most_one_seq(bool_vars):
    name = ''.join(random.choice(v) for i in range(30))
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

def exactly_one_seq(bool_vars):
    return And(at_least_one_seq(bool_vars), at_most_one_seq(bool_vars))


# Bitwise
def toBinary(num, length = None):
    num_bin = bin(num).split("b")[-1]
    if length:
        return "0"*(length - len(num_bin)) + num_bin
    return num_bin
    
def at_least_one_bw(bool_vars):
    return at_least_one_np(bool_vars)

def at_most_one_bw(bool_vars):
    name = ''.join(random.choice(v) for i in range(30))
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

def exactly_one_bw(bool_vars):
    return And(at_least_one_bw(bool_vars), at_most_one_bw(bool_vars)) 


# Heule
def at_least_one_he(bool_vars):
    return at_least_one_np(bool_vars)

def at_most_one_he(bool_vars):
    name = ''.join(random.choice(v) for i in range(30))
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


def plot_device(model, plate, w: int, h: int, n_chips, img_path=""):

    """
    Create, save or show an image of the predicted plate when rotation is allowed

    Parameters
    ----------
    pos_x: list
        The x positions of the chips
    pos_y: list
        The y positions of the chips
    widths: list
        The chip's widths
    heights: list
        The chip's height
    w: int
        The plate width
    h: int
        The plate height
    rotations:
        An array of bool reporting the rotated chips
    img_path:
        The path where the image will be saved, if not specified the image will be shown but not saved.
        It can be string or Path.

    """
    colors = {}
    for k in range(n_chips):
        colors[k] = (randint(0,100)/100, randint(0,100)/100, randint(0,100)/100)

    fig, ax = plt.subplots()
    ax.axis([0, w, 0, h])
    for y in range(h):
        for x in range(w):
            for k in range(n_chips):
                if model.evaluate(plate[y][x][k]):
                    rect = Rectangle(
                        (x, y),
                        1, 1,
                        facecolor=colors[k],
                        edgecolor=(0,0,0),
                        linewidth=2,
                    )
                    ax.add_patch(rect)
    if img_path == "":
        plt.show()
    else:
        if (os.path.isfile(img_path)) or not os.path.isfile(img_path):
            print(img_path)
            plt.savefig(img_path)

    plt.close()
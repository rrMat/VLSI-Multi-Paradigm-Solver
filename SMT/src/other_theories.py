from pysmt.typing import *
from pysmt.shortcuts import *

import numpy as np
import matplotlib.pyplot as plt
import os
from random import randint
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import time
from itertools import combinations
import utils.utils as ut
import sexpr

i = 1
f = ut.load_data(i)
w = f[0]
n = f[1]
chip_w = f[2].tolist()
chip_h = f[3].tolist()
min_h = sum([chip_w[k] * chip_h[k] for k in range(n)]) // w
max_h = sum(chip_h)
print("current i", i)
print(w, n, min_h, max_h, chip_w, chip_h)

h = min_h

x_position = [Symbol(f"x_pos{s}", INT) for s in range(n)]
y_position = [Symbol(f"y_pos{s}", INT) for s in range(n)]


          
        


with Solver(name="z3") as solver:
    solver.add_assertion(And([And(0 <= x_position[i], x_position[i] <= w - chip_w[i])
                             for i in range(n)]))

    solver.add_assertion(And([And(0 <= y_position[i], y_position[i] <= h - chip_h[i])
                              for i in range(n)]))

    for (i,j) in combinations(range(n), 2):
              solver.add_assertion(Or(y_position[i] + chip_h[i] <= y_position[j],
                                       y_position[j] + chip_h[j] <= y_position[i],
                                       x_position[i] + chip_w[i] <= x_position[j],
                                       x_position[j] + chip_w[j] <= x_position[i]))



    if not solver.solve():
        print("Domain is not SAT!!!")
        exit()
    else:

        m = solver.get_model()
        print(m)
        x_pos = []
        for i in range(n):
            x_pos.append(m[x_position[i]])
        y_pos = []
        for i in range(n):
            y_pos.append(m[y_position[i]])


print(x_pos)
print(y_pos)
print(min_h)
 
print(type(y_pos[1]._content[2]))

def ToInt(element):
    new_list = []
    for i in range(len(element)):
        new_list.append(element[i]._content[2])   
    return new_list



out_pat = os.path.join(
    os.path.dirname(__file__),
    '../out_img/plot' + str(57) + '.png'
    )

ut.plot_device(pos_x= ToInt(x_pos), pos_y = ToInt(y_pos), widths=  chip_w, heights = chip_h, w= w, 
h= min_h,  img_path=out_pat,  rotations = [] )






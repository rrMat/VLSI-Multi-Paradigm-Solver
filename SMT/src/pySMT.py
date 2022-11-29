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
import multiprocessing

def free_solver(w, n, min_h, max_h, chip_w, chip_h, Theo):
    start_time = time.time()
    x_position = [Symbol(f"x_pos{s}", INT) for s in range(n)]
    y_position = [Symbol(f"y_pos{s}", INT) for s in range(n)]

    for h in range(min_h, max_h + 1):
        
        print("current h: ", h)
        with Solver(name=Theo) as solver:

            #Constrains
            ##Boundaries
            solver.add_assertion(And([And(0 <= x_position[i], x_position[i] <= w - chip_w[i])
                                    for i in range(n)]))

            solver.add_assertion(And([And(0 <= y_position[i], y_position[i] <= h - chip_h[i])
                                    for i in range(n)]))

            ##No Overlap
            for (i,j) in combinations(range(n), 2):
                    solver.add_assertion(Or(y_position[i] + chip_h[i] <= y_position[j],
                                            y_position[j] + chip_h[j] <= y_position[i],
                                            x_position[i] + chip_w[i] <= x_position[j],
                                            x_position[j] + chip_w[j] <= x_position[i]))

            # ##Cumulatively on the columns
            # for u in range(w):
            #     solver.add_assertion(LE(Plus([Ite(And(x_position[i] <= u, u < x_position[i] + chip_w[i]), chip_h[i], 0) for i in range(n)]), h))
            


            #  #symmetry breaking
            # def precedes(a1, a2):
            #     if not a1:
            #         return TRUE
            #     if not a2:
            #         return FALSE
            #     return Or(a1[0] <= a2[0], And(a1[0] == a2[0], precedes(a1[1:], a2[1:])))
          
            # solver.add_assertion( precedes(y_position,[h - y_position[i] - chip_h[i] for i in range(0, len(y_position))] ))


            # solver.add_assertion( precedes(x_positions,[w - x_positions[i] - chip_w[i] for i in range(0, len(x_positions))] ))


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
                elapsed_time = time.time() - start_time
                print(f'{elapsed_time * 1000:.1f} ms')
                return m, x_pos, y_pos, h, elapsed_time


def ToInt(element):
    new_list = []
    for i in range(len(element)):
        new_list.append(element[i]._content[2])   
    return new_list

tim = []
Theo = ["z3", "cvc4", "yices", "btor", "picosat", "bdd"]
for i in range(1,10):
    f = ut.load_data(i)
    w = f[0]
    n = f[1]
    chip_w = f[2].tolist()
    chip_h = f[3].tolist()
    min_h = sum([chip_w[k] * chip_h[k] for k in range(n)]) // w
    max_h = sum(chip_h)
    print("current i", i)
    print(w, n, min_h, max_h, chip_w, chip_h)

    resul = free_solver(w, n, min_h, max_h, chip_w, chip_h, Theo[1])
    if resul != None:
        sol_path = os.path.join(
            os.path.dirname(__file__),
            '../out/pySMT/sol' + str(i) + ".txt"
        )
        tim.append((i, resul[4]))
    else:
        tim.append((i, False))

    if resul != None:
        out_pat = os.path.join(
            os.path.dirname(__file__),
            '../out_img/pySMT' + str(i) + '.png'
            )
        ut.plot_device(pos_x= ToInt(resul[1]), pos_y = ToInt(resul[2]), widths=  chip_w, heights = chip_h, w= w, 
            h= resul[3],  img_path=out_pat,  rotations = [] )
        

txt_path = os.path.join(
os.path.dirname(__file__),
'../timings/pySMT.csv'
)

np.savetxt(txt_path, tim, fmt = "%f")

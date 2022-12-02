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
    rotations = [Symbol(f"rotations{i}", BOOL) for i in range(n)]
    chip_h_true = [Symbol(f"chip_h_true{i}", INT) for i in range(n)]
    chip_w_true = [Symbol(f"chip_w_true{i}", INT) for i in range(n)]       

    for h in range(min_h, max_h + 1):
        
        print("current h: ", h)
        with Solver(name=Theo) as solver:

            #Constrains

            #Rotation 
            solver.add_assertion([Xor(
                And(rotations[i],
                    Equals(chip_w_true[i],chip_h[i]),
                    Equals(chip_h_true[i],chip_w[i])),
                And(Not(rotations[i]),
                    Equals(chip_w_true[i], chip_w[i]),
                    Equals(chip_h_true[i], chip_h[i])))
                for i in range(n)])
            
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

            
            if not solver.solve():
                print("Domain is not SAT!!!")
                continue
            else:

                m = solver.get_model()
                print(m)
                x_pos = []
                for i in range(n):
                    x_pos.append(m[x_position[i]])
                y_pos = []
                for i in range(n):
                    y_pos.append(m[y_position[i]])
                rot = []
                for i in range(n):
                    rot.append(m[rotations[i]])
                elapsed_time = time.time() - start_time
                print(f'{elapsed_time * 1000:.1f} ms')
                return m, x_pos, y_pos, h, elapsed_time, rot


def ToInt(element):
    new_list = []
    for i in range(len(element)):
        new_list.append(element[i]._content[2])   
    return new_list

tim = []
Theo = ["z3",  "msat"]
choseen_theory = 1
for i in range(39,40):
    f = ut.load_data(i)
    w = f[0]
    n = f[1]
    chip_w = f[2].tolist()
    chip_h = f[3].tolist()
    min_h = sum([chip_w[k] * chip_h[k] for k in range(n)]) // w
    max_h = sum(chip_h)
    print("current i", i)
    print(w, n, min_h, max_h, chip_w, chip_h)

    resul = free_solver(w, n, min_h, max_h, chip_w, chip_h, Theo[choseen_theory])
    if resul != None:
        sol_path = os.path.join(
            os.path.dirname(__file__),
            '../out/pySMT_rotation/sol' + str(Theo[choseen_theory])+ str(i) + ".txt"
            
        )
        tim.append((i, resul[4]))
        ut.write_sol(sol_path, w, resul[3]-1, n, chip_w, chip_h, ToInt(resul[1]), ToInt(resul[2]),  rotation =  [])
    else:
        tim.append((i, False))

    if resul != None:
        out_pat = os.path.join(
            os.path.dirname(__file__),
            '../out_img/pySMT_rotation' + str(Theo[choseen_theory])+ "_" + str(i) + '.png'
            )
        ut.plot_device(pos_x= ToInt(resul[1]), pos_y = ToInt(resul[2]), widths=  chip_w, heights = chip_h, w= w, 
            h= resul[3],  img_path=out_pat,  rotations = [] )
        

txt_path = os.path.join(
os.path.dirname(__file__),
'../timings/pySMT_rotation' + str(Theo[choseen_theory])+ '.csv'
)

np.savetxt(txt_path, tim, fmt = "%f")

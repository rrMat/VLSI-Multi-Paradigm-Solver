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

class pySMT_z3:
    def __init__(self):
        pass    

    def free_solver(self, w, n, min_h, max_h, chip_w, chip_h):
        start_time = time.time()
        x_position = [Symbol(f"x_pos{s}", INT) for s in range(n)]
        y_position = [Symbol(f"y_pos{s}", INT) for s in range(n)]

        for h in range(min_h, max_h):
            with Solver('z3') as solver:

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

                
                if not solver.solve():
                    print("Domain is not SAT!!!")
                    continue
                else:

                    m = solver.get_model()
                    
                    x_pos = []
                    for i in range(n):
                        x_pos.append(m[x_position[i]])
                    y_pos = []
                    for i in range(n):
                        y_pos.append(m[y_position[i]])
                    elapsed_time = time.time() - start_time
                    
                    return m, x_pos, y_pos, h, elapsed_time



    def execute(self, _, i, return_dict):

        def ToInt(element):
            new_list = []
            for i in range(len(element)):
                new_list.append(element[i]._content[2])   
            return new_list


        txt_path = os.path.join(
        os.path.dirname(__file__),
        '../timings/pySMT' + "_z3" + '.csv'
        )
        
        sol_path = os.path.join(
                os.path.dirname(__file__),
                '../out/pySMT_z3/sol' + "z3" + str(i) + ".txt"
                
            )

        out_pat = os.path.join(
                os.path.dirname(__file__),
                '../out_img/pySMT' + "z3" + "_" + str(i) + '.png'
                )

        return_dict["solved"] = False
        return_dict["sol_path"] = sol_path
        return_dict["out_pat"] = out_pat

        f = ut.load_data(i)
        w = f[0]
        n = f[1]
        chip_w = f[2].tolist()
        chip_h = f[3].tolist()
        min_h = sum([chip_w[k] * chip_h[k] for k in range(n)]) // w
        max_h = sum(chip_h)
    

        return_dict["txt_path"] = txt_path
        return_dict["w"] = w
        return_dict["n"] = n
        return_dict["chip_w"] = chip_w
        return_dict["chip_h"] = chip_h
        return_dict["rotation"] = []
        return_dict["height"] = min_h


        resul = self.free_solver(w, n, min_h, max_h, chip_w, chip_h)


        if resul != None:
            return_dict["height"] = resul[3]
            return_dict["time"] = resul[4]
            return_dict["x_pos"] = ToInt(resul[1])
            return_dict["y_pos"] = ToInt(resul[2])
            return_dict["rotation"] = []


     
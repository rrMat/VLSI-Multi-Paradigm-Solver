import numpy as np
from z3 import *
import matplotlib.pyplot as plt
import os
from random import randint
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import time
from itertools import combinations
import utils.utils as ut

class z3Py_rotation:
    
    def __init__(self):
        pass

    def plate(self, w, n, min_h, max_h, chip_w, chip_h):
        start_time = time.time()
        #VAR
        x_position = [Int(f"x_pos{i}") for i in range(n)]
        y_position = [Int(f"y_pos{i}") for i in range(n)]
        rotations = [Bool(f"rotations{i}") for i in range(n)]
        chip_h_true = [Int(f"chip_h_true{i}") for i in range(n)]
        chip_w_true = [Int(f"chip_w_true{i}") for i in range(n)]       

        
        for h in range(min_h, max_h + 1):

                print("current h: ", h)

                s = Solver()
                # CONSTRAINTS


                # c0) ROTATION
                s.add([Xor(
                      And(rotations[i],
                          chip_w_true[i] == chip_h[i],
                          chip_h_true[i] == chip_w[i]),
                      And(Not(rotations[i]),
                          chip_w_true[i] == chip_w[i],
                          chip_h_true[i] == chip_h[i]))
                      for i in range(n)])



                #domani bounds
                s.add([And(0 <= x_position[i], x_position[i] <= w - chip_w_true[i])
                                  for i in range(n)])
                
                s.add([And(0 <= y_position[i], y_position[i] <= h - chip_h_true[i])
                                  for i in range(n)])
                
                #cumulatively on the rows
                for u in range(h):
                  s.add(
                      w >= Sum([If(And(y_position[i] <= u, u < y_position[i] + chip_h_true[i]),
                                            chip_w_true[i], 0) for i in range(n)]))
                
                
                #cumulatively on the columns
                for u in range(w):
                      s.add(h >= Sum([If(And(x_position[i] <= u, u < x_position[i] + chip_w_true[i]),
                                                  chip_h_true[i], 0) for i in range(n)]))
              
              
                #overlap
                for (i,j) in combinations(range(n), 2):
                    s.add(Or(y_position[i] + chip_h_true[i] <= y_position[j],
                                            y_position[j] + chip_h_true[j] <= y_position[i],
                                            x_position[i] + chip_w_true[i] <= x_position[j],
                                            x_position[j] + chip_w_true[j] <= x_position[i]))



                def precedes(a1, a2):
                  if not a1:
                    return True
                  if not a2:
                    return False
                  return Or(a1[0] <= a2[0], And(a1[0] == a2[0], precedes(a1[1:], a2[1:])))
                
                
                s.add( precedes(y_position,[h - y_position[i] - chip_h_true[i] for i in range(0, len(y_position))] ))
                s.add( precedes(x_position,[w - x_position[i] - chip_w_true[i] for i in range(0, len(x_position))] ))


                if s.check() != sat:
                  print(s.check())
                  continue
                else:
                  m = s.model()
                  x_pos = []
                  for i in range(n):
                    x_pos.append(m[x_position[i]].as_long())
                  y_pos = []
                  for i in range(n):
                    y_pos.append(m[y_position[i]].as_long())
                  rot = []
                  for i in range(n):
                    rot.append(m[rotations[i]])
                  elapsed_time = time.time() - start_time
                  print(f'{elapsed_time * 1000:.1f} ms')
                  return m, x_pos, y_pos, h, elapsed_time, rot


    def execute(self, _,i, return_dict):

        txt_path = os.path.join(
            os.path.dirname(__file__),
            '../Timings_rotation/z3Py_rotation.csv'
        )

        sol_path = os.path.join(
            os.path.dirname(__file__),
            '../out/z3Py_rotation/sol' + str(i) + ".txt"
        )

        
        out_path = os.path.join(
            os.path.dirname(__file__),
            '../out_img/z3Py_rotation' + str(i) + ".png"
        )

        return_dict["solved"] = False
        return_dict["sol_path"] = sol_path
        return_dict["out_pat"] = out_path


        f = ut.load_data(i)
        w = f[0]
        n = f[1]
        chip_w = f[2].tolist()
        chip_h = f[3].tolist()
        min_h = sum([chip_w[k] * chip_h[k] for k in range(n)]) // w
        max_h = sum(chip_h)
        print("current i", i)

        return_dict["txt_path"] = txt_path
        return_dict["w"] = w
        return_dict["n"] = n
        return_dict["chip_w"] = chip_w
        return_dict["chip_h"] = chip_h
        return_dict["height"] = min_h
        return_dict["rotation"] = []

        resul = self.plate(w, n, min_h, max_h, chip_w, chip_h)

        if resul != None:
            return_dict["height"] = resul[3]
            return_dict["time"] = resul[4]
            return_dict["x_pos"] = resul[1]
            return_dict["y_pos"] = resul[2]

            to_str = [resul[5][i].sexpr() for i in range(n)]
            to_bool = []
            for i in range(0,len(to_str)):
                  if to_str[i] == "false":
                        to_bool.append(False)
                  else: to_bool.append(True)

            return_dict["rotation"] = to_bool

        # if resul != None:
        #   sol_path = os.path.join(
        #     os.path.dirname(__file__),
        #     '../out/z3Py_rotation/sol' + str(i) + ".txt"
        #   )
        #   tim.append(resul[4])
          
        #   ut.write_sol(sol_path, w, resul[3], n, chip_w, chip_h, resul[1], resul[2], rotation= to_bool)
        #   ut.write_stat_line(txt_path, i, resul[3], time = resul[4], solution_type = "optimal")
        # else:
        #   tim.append(False)
        #   ut.write_stat_line(txt_path, i, resul[3], time = resul[4], solution_type = "UNSAT" )


        # if resul != None:

          
        #   ut.plot_device(resul[1], resul[2], chip_w, chip_h, w, resul[3]-1,  to_bool ,img_path=out_path)



        




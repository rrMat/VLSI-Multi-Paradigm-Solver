import numpy as np
from z3 import *
import matplotlib.pyplot as plt

from random import randint
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import time
from itertools import combinations
import utils.utils as ut




class z3Py_parallel_rotation:

    def __init__(self):
      pass

    def plate(self, w, n, min_h, max_h, chip_w, chip_h):
      start_time = time.time()
      #VAR
      x_positions = [Int(f"x_pos{i}") for i in range(n)]
      y_positions = [Int(f"y_pos{i}") for i in range(n)]
      rotations = [Bool(f"rotations{i}") for i in range(n)]
      chip_h_true = [Int(f"chip_h_true{i}") for i in range(n)]
      chip_w_true = [Int(f"chip_w_true{i}") for i in range(n)]   

      #s
      s = SolverFor("QF_LIA")
      
      #Try to implement Parallelism
      set_option("parallel.enable", True)
      set_option("parallel.threads.max", 16)

      for h in range(min_h, max_h):
              print("current h: ", h - 1)
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
              s.add([And(0 <= x_positions[i], x_positions[i] <= w - chip_w[i])
                                for i in range(n)])
              
              s.add([And(0 <= y_positions[i], y_positions[i] < h - chip_h[i])
                                for i in range(n)])
              
              #cumulatively on the rows
              for u in range(h):
                s.add(
                    w >= Sum([If(And(y_positions[i] <= u, u < y_positions[i] + chip_h[i]),
                                          chip_w[i], 0) for i in range(n)]))
              
              
              #cumulatively on the columns
              for u in range(w):
                    s.add(h >= Sum([If(And(x_positions[i] <= u, u < x_positions[i] + chip_w[i]),
                                                chip_h[i], 0) for i in range(n)]))
            
            
              #overlap
              for (i,j) in combinations(range(n), 2):
                  s.add(Or(y_positions[i] + chip_h[i] <= y_positions[j],
                                          y_positions[j] + chip_h[j] <= y_positions[i],
                                          x_positions[i] + chip_w[i] <= x_positions[j],
                                          x_positions[j] + chip_w[j] <= x_positions[i]))


              #symmetry breaking
              #the strict one seems to perform worst
              def precedes(a1, a2):
                if not a1:
                  return True
                if not a2:
                  return False
                return Or(a1[0] <= a2[0], And(a1[0] == a2[0], precedes(a1[1:], a2[1:])))
              
              s.add( precedes(y_positions,[h - y_positions[i] - chip_h[i] for i in range(0, len(y_positions))] ))
              s.add( precedes(x_positions,[w - x_positions[i] - chip_w[i] for i in range(0, len(x_positions))] ))

              

                  
              if s.check() != sat:
                print("Took too long")
                continue
              else:
                m = s.model()
                x_pos = []
                for i in range(n):
                  x_pos.append(m[x_positions[i]].as_long())
                y_pos = []
                for i in range(n):
                  y_pos.append(m[y_positions[i]].as_long())
                rot = []
                for i in range(n):
                  rot.append(m[rotations[i]])
                elapsed_time = time.time() - start_time
                print(f'{elapsed_time * 1000:.1f} ms')
                return m, x_pos, y_pos, h, elapsed_time, rot

    def execute(self, _, i, return_dict):

        txt_path = os.path.join(
          os.path.dirname(__file__),
          '../Timings_rotation/z3Py_parallel_rotation.csv'
        )

        sol_path = os.path.join(
            os.path.dirname(__file__),
            '../out/z3Py_parallel_rotation/sol' + str(i) + ".txt"
        )

        out_pat = os.path.join(
            os.path.dirname(__file__),
            '../out_img/z3Py_parallel_rotation' + str(i) + '.png'
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
        print("current i", i)

        return_dict["height"] = min_h
        return_dict["txt_path"] = txt_path
        return_dict["n"] = n
        return_dict["chip_w"] = chip_w
        return_dict["chip_h"] = chip_h
        return_dict["w"] = w
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
          
        #   tim.append(resul[4])
        #   to_str = [resul[5][i].sexpr() for i in range(n)]
        #   to_bool = []
        #   for i in range(0,len(to_str)):
        #         if to_str[i] == "false":
        #               to_bool.append(False)
        #         else: to_bool.append(True)
        #   ut.write_sol(sol_path, w, resul[3], n, chip_w, chip_h, resul[1], resul[2],  rotation =  to_bool)
        #   ut.write_stat_line(txt_path, i, resul[3], time = resul[4], solution_type = "optimal")
        # else:
        #   tim.append(False)
        #   ut.write_stat_line(txt_path, i, resul[3], time = resul[4], solution_type = "UNSAT" )

        # 
          
        #   ut.plot_device(pos_x= resul[1], pos_y = resul[2], widths=  chip_w, heights = chip_h, w= w, 
        #   h= resul[3]-1,  img_path=out_pat,  rotations = to_bool )

    

    

   
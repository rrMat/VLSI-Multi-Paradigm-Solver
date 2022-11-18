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


time_available = 300000

def plate(w, n, min_h, max_h, chip_w, chip_h):
  start_time = time.time()
  #VAR
  x_positions = [Int(f"x_pos{i}") for i in range(n)]
  y_positions = [Int(f"y_pos{i}") for i in range(n)]
  rotations = [Bool(f"rotations{i}") for i in range(n)]
  chip_h_true = [Int(f"chip_h_true{i}") for i in range(n)]
  chip_w_true = [Int(f"chip_w_true{i}") for i in range(n)]       

  #s
  
    

  for h in range(min_h + 1, min_h + 2):
          time_remained = time_available - (time.time() - start_time)
          if time_remained <= 1:
            print("Took too long")
            break
          print("current h: ", h - 1)

          s = Solver()
          s.set("timeout", int(time_remained))
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
          s.add([And(0 <= x_positions[i], x_positions[i] <= w - chip_w_true[i])
                             for i in range(n)])
          
          s.add([And(0 <= y_positions[i], y_positions[i] < h - chip_h_true[i])
                             for i in range(n)])
          
          #cumulatively on the rows
          for u in range(h):
            s.add(
                w >= Sum([If(And(y_positions[i] <= u, u < y_positions[i] + chip_h_true[i]),
                                      chip_w_true[i], 0) for i in range(n)]))
          
          
          #cumulatively on the columns
          for u in range(w):
                s.add(h >= Sum([If(And(x_positions[i] <= u, u < x_positions[i] + chip_w_true[i]),
                                             chip_h_true[i], 0) for i in range(n)]))
        
        
          #overlap
          for (i,j) in combinations(range(n), 2):
              s.add(Or(y_positions[i] + chip_h_true[i] <= y_positions[j],
                                       y_positions[j] + chip_h_true[j] <= y_positions[i],
                                       x_positions[i] + chip_w_true[i] <= x_positions[j],
                                       x_positions[j] + chip_w_true[j] <= x_positions[i]))


          # for i in range(1, n):
          #   for j in range(0, i):
          #       s.add(Or(y_positions[i] + chip_h_true[i] <= y_positions[j],
          #                           y_positions[j] + chip_h_true[j] <= y_positions[i],
          #                           x_positions[i] + chip_w_true[i] <= x_positions[j],
          #                           x_positions[j] + chip_w_true[j] <= x_positions[i]))

          #symmetry breaking
          #the strict one seems to perform worst
          def precedes(a1, a2):
            if not a1:
              return True
            if not a2:
              return False
            return Or(a1[0] <= a2[0], And(a1[0] == a2[0], precedes(a1[1:], a2[1:])))
          
          
          s.add( precedes(y_positions,[h - y_positions[i] - chip_h_true[i] for i in range(0, len(y_positions))] ))
          s.add( precedes(x_positions,[w - x_positions[i] - chip_w_true[i] for i in range(0, len(x_positions))] ))


          if s.check() != sat:
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




tim = []

for i in range(1,41):
    f = ut.load_data(i)
    w = f[0]
    n = f[1]
    chip_w = f[2].tolist()
    chip_h = f[3].tolist()
    min_h = sum([chip_w[k] * chip_h[k] for k in range(n)]) // w
    max_h = sum(chip_h)
    print("current i", i)
    resul = plate(w, n, min_h, max_h, chip_w, chip_h)

    if resul != None:
      sol_path = os.path.join(
        os.path.dirname(__file__),
        '../out/rotation/sol' + str(i) + ".txt"
      )
      tim.append((i, resul[4]))
      ut.write_sol(sol_path, w, resul[3]-1, n, chip_w, chip_h, resul[1], resul[2])
    else:
      tim.append((i, False))


    if resul != None:
      out_path = os.path.join(
        os.path.dirname(__file__),
        '../out_img/rotation_solver' + str(i) + ".png"
      )
      #This is the ugliest thing I have done in a long time. Yet it works and 
      #I couldn't figure out how to cast BoolRef to bool in a more reasonable way
      to_str = [resul[5][i].sexpr() for i in range(n)]
      to_bool = []
      for i in range(0,len(to_str)):
            if to_str[i] == "false":
                  to_bool.append(False)
            else: to_bool.append(True)
      ut.plot_device_rotation(resul[1], resul[2], chip_w, chip_h, w, resul[3]-1,  to_bool,img_path=out_path)



txt_path = os.path.join(
  os.path.dirname(__file__),
  '../timings/rotation_solver.csv'
)

np.savetxt(txt_path, tim, fmt = "%f")

# print(type())

# to = [resul[5][i].sexpr() for i in range(n)]
# ou = []
# for i in range(0,len(to)):
#   if to[i] == "false":
#     ou.append(False)
#   else: ou.append(True)

# print(ou)
# print(type(ou[1]))

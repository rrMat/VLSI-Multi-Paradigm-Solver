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



set_option(timeout=3)



def plate(w, n, min_h, max_h, chip_w, chip_h):
  start_time = time.time()
  #VAR
  x_positions = [Int(f"x_pos{i}") for i in range(n)]
  y_positions = [Int(f"y_pos{i}") for i in range(n)]

  #s
  
    
  for h in range(min_h + 1, max_h):
          print("current h: ", h - 1)
          # CONSTRAINTS
          #domani bounds

          s = Solver()
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
            break
          else:
            m = s.model()
            x_pos = []
            for i in range(n):
              x_pos.append(m[x_positions[i]].as_long())
            y_pos = []
            for i in range(n):
              y_pos.append(m[y_positions[i]].as_long())
            elapsed_time = time.time() - start_time
            print(f'{elapsed_time * 1000:.1f} ms')
            return m, x_pos, y_pos, h, elapsed_time


tim = []

for i in range(1,24):
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
      out_path = os.path.join(
        os.path.dirname(__file__),
        '../out_img/plot' + str(i) + ".png"
      )
      tim.append((i, resul[4]))
      ut.plot_device(resul[1], resul[2], chip_w, chip_h, w, resul[3]-1, img_path=out_path)
    else:
      tim.append((i, False))

txt_path = os.path.join(
  os.path.dirname(__file__),
  '../timings/solver.csv'
)

np.savetxt(txt_path, tim, fmt = "%f")
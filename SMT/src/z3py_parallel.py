import numpy as np
from z3 import *
import matplotlib.pyplot as plt

from random import randint
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import time
from itertools import combinations
import utils.utils as ut

#Try to implement Parallelism
set_option("parallel.enable", True)
set_option("parallel.threads.max", 16)

set_option(timeout=300000)



def plate(w, n, min_h, max_h, chip_w, chip_h):
  start_time = time.time()
  #VAR
  x_positions = [Int(f"x_pos{i}") for i in range(n)]
  y_positions = [Int(f"y_pos{i}") for i in range(n)]

  #s
  s = SolverFor("QF_LIA")
    

  for h in range(min_h + 1, min_h + 2):
          print("current h: ", h - 1)
          # CONSTRAINTS
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

for i in range(1,40):
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
        '../out/z3Py_parallel/sol' + str(i) + ".txt"
      )
      tim.append((i, resul[4]))
      ut.write_sol(sol_path, w, resul[3]-1, n, chip_w, chip_h, resul[1], resul[2],  rotation =  [])
    else:
      tim.append((i, False))

    if resul != None:
      out_pat = os.path.join(
        os.path.dirname(__file__),
        '../out_img/z3Py_parallel' + str(i) + '.png'
      )
      ut.plot_device(pos_x= resul[1], pos_y = resul[2], widths=  chip_w, heights = chip_h, w= w, 
      h= resul[3]-1,  img_path=out_pat,  rotations = [] )

 

txt_path = os.path.join(
  os.path.dirname(__file__),
  '../timings/z3Py_parallel.csv'
)

np.savetxt(txt_path, tim, fmt = "%f")
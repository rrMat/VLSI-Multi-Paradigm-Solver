import numpy as np
import os


txt_path = os.path.join(
        os.path.dirname(__file__),
        '../timings/plot.csv'
      )


tim = [2,1]

np.savetxt(txt_path, tim, fmt = "%f")
print(txt_path)
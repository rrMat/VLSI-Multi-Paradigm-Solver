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

X = IntVector('x', 5)
Y = RealVector('y', 5)
P = BoolVector('p', 5)

print([ y**2 for y in Y ])
print(Sum([ y**2 for y in Y ]))
import numpy as np
from z3 import *
import matplotlib.pyplot as plt

from random import randint
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import time
from itertools import combinations
import utils as utils

solver = SolverFor("QF_BV")
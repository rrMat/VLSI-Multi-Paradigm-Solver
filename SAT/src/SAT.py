from itertools import combinations
import math
import time
import os
from tqdm import tqdm
import numpy as np
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(base_dir)
sys.path.append(base_dir)
import VLSISolver
import sat_utils
import utils


OVERRIDE = True
INTERRUPT = True
PRINT = False
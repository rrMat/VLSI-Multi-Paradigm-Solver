from z3 import *
import math
import numpy as np 
import time
import utils.utils as utils
import multiprocessing
import os
from SMT.src.z3Py import z3Py
from SMT.src.z3Py_rotation import z3Py_rotation
from SMT.src.z3Py_parallel_rotation import z3Py_parallel_rotation
from SMT.src.z3Py_parallel import z3Py_parallel
from SMT.src.pySMT_z3 import pySMT_z3
from SMT.src.pySMT_msat import pySMT_msat
from SMT.src.analysis import analysis


class SMTSolver:

    TIME_AVAILABLE = 300000

    MODELS = {
        'analysis' : analysis,
        'pySMT_z3' : pySMT_z3,
        'pySMT_msat' : pySMT_msat,
        'z3Py': z3Py,
        'z3Py_rotation' : z3Py_rotation,
        'z3Py_parallel_rotation' : z3Py_parallel_rotation,
        'z3Py_parallel' : z3Py_parallel,
    }

    def __init__(self, model_name):
        self.model_name = model_name

    def execute(self):
        model = self.MODELS[self.model_name]()

        manager = multiprocessing.Manager()
        p = multiprocessing.Process(target=model.execute)
        p.start()
        p.join(self.TIME_AVAILABLE)
        if p.is_alive():
            p.terminate()
            p.join()

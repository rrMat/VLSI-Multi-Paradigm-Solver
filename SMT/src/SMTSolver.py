from z3 import *
import math
import numpy as np 
import time
import utils.utils as utils
import multiprocessing
import os
from SMT.src.z3Py import z3Py

class SMTSolver:

    TIME_AVAILABLE = 300000

    MODELS = {
        'z3Py': z3Py
    }

    def __init__(self, model_name):
        self.model_name = model_name

    def execute(self):
        model = self.MODELS[self.model_name]()

        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        p = multiprocessing.Process(target=model.execute)
        p.start()
        p.join(self.TIME_AVAILABLE)
        if p.is_alive():
            p.terminate()
            p.join()

from z3 import *
import math
import numpy as np 
import time
import utils.utils as utils
import multiprocessing
import os
from SMT.src.z3Py import z3Py
from SMT.src.z3Py_rotation import z3Py_rotation
from SMT.src.z3Py_parallel import z3Py_parallel
from SMT.src.pySMT_z3 import pySMT_z3
from SMT.src.pySMT_msat import pySMT_msat
import utils.utils as ut


class SMTSolver:

    TIME_AVAILABLE = 300

    MODELS = {
        'pySMT_z3' : pySMT_z3,
        'pySMT_msat' : pySMT_msat,
        'z3Py': z3Py,
        'z3Py_rotation' : z3Py_rotation,
        'z3Py_parallel' : z3Py_parallel,
    }

    def __init__(self, model_name, instance, print_img, verbose):
        self.model_name = model_name
        self.instance = instance
        self.print_img = print_img
        self.verbose = verbose

    def execute(self):
        model = self.MODELS[self.model_name]()

        if self.instance:
            for i in range(self.instance,self.instance+1):
                    manager = multiprocessing.Manager()
                    return_dict = manager.dict()
                    p = multiprocessing.Process(target=model.execute, args = (1, i, return_dict))
                    p.start()
                    p.join(self.TIME_AVAILABLE)
                    if len(return_dict) != 10:
                        ut.write_sol(return_dict["sol_path"] , return_dict["w"], return_dict["height"],
                        return_dict["n"], return_dict["chip_w"], return_dict["chip_h"], return_dict["x_pos"], return_dict["y_pos"],  rotation =  return_dict["rotation"])
                        ut.write_stat_line(return_dict["txt_path"], i, return_dict["height"], time = return_dict["time"],
                        solution_type = "optimal")
                        if self.print_img == True:
                            ut.plot_device(pos_x= return_dict["x_pos"], pos_y = return_dict["y_pos"], widths=  return_dict["chip_w"], 
                            heights = return_dict["chip_h"], w= return_dict["w"], 
                            h= return_dict["height"],  img_path=return_dict["out_pat"],  rotations = return_dict["rotation"] )
                        if self.verbose:
                            print("Current i", self.instance)
                            print(f'{return_dict["time"] * 1000:.1f} ms')
                            print("The height is ", return_dict["height"])
                    else:
                        if self.verbose:
                            print("Current i", self.instance)   
                        ut.write_stat_line(return_dict["txt_path"], i, return_dict["height"], time = 300, solution_type = "UNSAT" )
                    
                    if p.is_alive():
                        p.terminate()
                        p.join()
        else:
            for i in range(1,40):
                    manager = multiprocessing.Manager()
                    return_dict = manager.dict()
                    p = multiprocessing.Process(target=model.execute, args = (1, i, return_dict))
                    p.start()
                    p.join(self.TIME_AVAILABLE)
                    if len(return_dict) != 10:
                        ut.write_sol(return_dict["sol_path"] , return_dict["w"], return_dict["height"],
                        return_dict["n"], return_dict["chip_w"], return_dict["chip_h"], return_dict["x_pos"], return_dict["y_pos"],  rotation =  return_dict["rotation"])
                        ut.write_stat_line(return_dict["txt_path"], i, return_dict["height"], time = return_dict["time"],
                        solution_type = "optimal")
                        if self.print_img == True:
                            ut.plot_device(pos_x= return_dict["x_pos"], pos_y = return_dict["y_pos"], widths=  return_dict["chip_w"], 
                            heights = return_dict["chip_h"], w= return_dict["w"], 
                            h= return_dict["height"],  img_path=return_dict["out_pat"],  rotations = return_dict["rotation"] )
                        if self.verbose:
                            print("Current i", i)
                            print(f'{return_dict["time"] * 1000:.1f} ms')
                            print("The height is ", return_dict["height"])
                    else:
                        if self.verbose:
                            print("Current i", i)
                        ut.write_stat_line(return_dict["txt_path"], i, return_dict["height"], time = 300, solution_type = "UNSAT" )
                    
                    if p.is_alive():
                        p.terminate()
                        p.join()
                

##########################
# @lorenzoTribuiani
# Novembre 2022

import time
import os
import csv
from datetime import timedelta
from minizinc import Solver, Instance, Model
from utils.utils import plot_device, load_data, write_sol


class CPSolver:

    def __init__(self, model: str=None, solver: str=None, rotation: bool=None, print_img:bool=False):

        self.__rotation = rotation
        self.__model = model
        self.__solver = solver
        self.__print_img = print_img
        self.__set_paths()
        

    def __set_paths(self):
        self.__stats_path = "CP/stats/{}/{}/out_data_{}.csv".format(
            "rotation" if self.__rotation else "no_rotation",
            self.__solver,
            self.__model
        )
        self.__model_path = "CP/src/solvers{}/MODEL_{}.mzn".format(
            "_rotation" if self.__rotation else "",
            self.__model.upper()
        )
        self.__img_path = "CP/img/{}/{}/{}/".format(
            "rotation" if self.__rotation else "no_rotation",
            self.__model.upper(),
            self.__solver
        )
        self.__out_path = "CP/out/{}/{}/{}/".format(
            "rotation" if self.__rotation else "no_rotation",
            self.__model.upper(),
            self.__solver
        )
        os.makedirs(os.path.dirname(self.__stats_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.__img_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.__out_path), exist_ok=True)


    def update_model(self, model: str):
        self.__model = model
        self.__set_paths()

    def update_rotation(self, rotation: bool):
        self.__rotation = rotation
        self.__set_paths()

    def update_solver(self, solver: str):
        self.__solver = solver
        self.__set_paths()


    def __solve(self, w: int, n: int, widths: list, heights: list):

        """
        Solve a single instance with the selected minizinc model

        Parameters
        ----------

        w: int
            The plate width
        n: int
            The number of chips
        widths: list
            The chips's widths
        Heights: int
            The chips's heights
        model_path: str
            The path of the minizinc model

        Returns
        -------

        x_pos: list
            The x positions of the chips
        y_pos: list
            The y positions of the chips
        w: int
            Pate width
        h: int
            Plate height
        widths: list
        height: list
        elapsed_time: float
            The time needed to find a solution
        """
        model = Model(self.__model_path)
        solver = Solver.lookup(self.__solver)

        inst = Instance(solver, model)
        inst["w"] = w
        inst["n"] = n
        inst["widths"] =widths
        inst["heights"] = heights

        start = time.time()
        out = inst.solve(timeout=timedelta(seconds=300), free_search=True)
        end = time.time()    

        x_pos = out.solution.positions_x
        y_pos = out.solution.positions_y
        h = out.solution.h

        if self.__rotation:
            rotations = out.solution.rotations
        else:
            rotations = []


        return (x_pos, y_pos, h, (end - start), rotations)



    def execute(self, index: int):

        """
        Execute the solving over a specific set of instances, prints data
        into a csv file and save the image

        Parameters
        ----------
        index: int
            The indtances index (if 0 is selected all the instances will be executed)


        """        
            
        if index is None:
            with open(self.__stats_path, mode="w", newline="") as file:
                header = ['device width', 'number of chips', "h", "solve time"]
                writer = csv.writer(file)
                writer.writerow(header)
                for i in range(1,41):

                    w, n, widths, heights = load_data(i)

                    print("Solving instance {} with {} model and {} solver...".format(
                        i,
                        self.__model.upper(),
                        self.__solver
                    ), end="", flush=True)

                    (pos_x, pos_y, h, elapsed_time, rotations) = self.__solve(
                        w,
                        n,
                        widths,
                        heights
                    )
                    print("Solved in: {} s".format(elapsed_time))
                    data = [w, n, h, elapsed_time]
                    writer.writerow(data)
                    
                    write_sol(
                        self.__out_path + "/solution-" + str(i) + ".txt",
                        w,
                        h,
                        n,
                        widths,
                        heights,
                        pos_x,
                        pos_y
                    )

                    if self.__print_img:
                        plot_device(pos_x, pos_y, widths, heights, w, h, rotations, self.__img_path +'device-' + str(i) +'.png')

        else:
            w, n, widths, heights = load_data(index)
            (pos_x, pos_y, h, elapsed_time, rotations) = self.__solve(
                w,
                n,
                widths,
                heights
            )
            
            print("Minimun Height Found: {}".format(h))
            print("Solve Time: {}".format(elapsed_time))
            print("--------------------------------")
            print()

            if self.__print_img:
                plot_device(pos_x, pos_y, widths, heights, w, h, rotations, self.__img_path + '/device-' + str(index) +'.png')






##########################
# @lorenzoTribuiani
# Novembre 2022

import time
import os
import csv
from datetime import timedelta
from minizinc import Solver, Instance, Model
from utils.utils import plot_device, load_data, write_sol, write_stat_line


class CPSolver:

    acceptable_models = ["std", "cml", "syb"]
    acceptable_solvers = ["chuffed", "gecode", "or-tools"]

    def __init__(self, model: str=None, solver: str=None, rotation: bool=False, print_img:bool=False):

        self.__rotation = rotation
        self.__model = model
        self.__solver = solver
        self.__print_img = print_img
        self.__set_paths()
        
    # create and updates paths value base on rotation, model and solver selected
    def __set_paths(self):

        if self.__solver is not None and self.__solver is not None:
            self.__stats_path = "CP/stats/{}/{}/out_data_{}.csv".format(
                "rotation" if self.__rotation else "no_rotation",
                self.__solver,
                self.__model
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

        if self.__model is not None:
            self.__model_path = "CP/src/solvers{}/MODEL_{}.mzn".format(
                "_rotation" if self.__rotation else "",
                self.__model.upper()
            )   

    def update_model(self, model: str):
        '''
        Update selected model. Creates (if needed) and updates paths.

        Parameters
        ----------
        model: str
            the new model, value accepted: max | sbs
        '''
        if model in self.acceptable_models:
            self.__model = model
            self.__set_paths()

    def update_rotation(self, rotation: bool):
        self.__rotation = rotation
        self.__set_paths()

    def update_solver(self, solver: str):
        '''
        Update selected solver. Creates (if needed) and updates paths.

        Parameters
        ----------
        solver: str
            the new solver, value accepted: chuffed | gecode
        '''
        if solver in self.acceptable_solvers:
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
            The widths of the chips
        height: list
            The heights of the chips
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
        
        try:
            x_pos = out.solution.X
            y_pos = out.solution.Y
            h = out.solution.h

            if self.__rotation:
                rotations = out.solution.rotations
            else:
                rotations = []
        
        # chatch for no solution found
        except:
            raise Exception()

        return (x_pos, y_pos, h, (end - start), rotations)



    def execute(self, index: int):

        """
        Execute the solving over a specific set of instances, prints data
        into a csv file and save the image

        Parameters
        ----------
        index: int
            The indtances index (if index is None all the instances will be executed)


        """        

        # execute on all instances    
        if index is None:

            print("\nStarting solving with {} model and {} solver:".format(
                self.__model.upper(),
                self.__solver
            ))
            print("---------------------------------------------------")
            print()

            for i in range(1,41):

                solution_type = ""
                w, n, widths, heights = load_data(i)

                print("Solving ins-{}...".format(i), end="", flush=True)
                
                try:
                    (pos_x, pos_y, h, elapsed_time, rotations) = self.__solve(
                        w,
                        n,
                        widths,
                        heights
                    )
                    # Optimal solution
                    if elapsed_time < 300:
                        print("solved in: {} s".format(elapsed_time))
                        solution_type = "optimal"
                    # non-optimal solution
                    else:
                        print("process Terminated, non-optimal solution found")
                        solution_type = "non-optimal"

                    write_sol(
                        self.__out_path + "/solution-" + str(i) + ".txt",
                        w,
                        h,
                        n,
                        widths,
                        heights,
                        pos_x,
                        pos_y,
                        rotations
                    )                      

                    if self.__print_img:
                        plot_device(pos_x, pos_y, widths, heights, w, h, rotations, self.__img_path +'device-' + str(i) +'.png')
                
                # no solution found within 5 mins
                except:
                    print("process terminated, no solution found")
                    h = ""
                    elapsed_time = 300
                    solution_type = "N|A"
                
                write_stat_line(
                        self.__stats_path,
                        i,
                        h,
                        elapsed_time,
                        solution_type
                    )                     
        
        # Execution on single instance
        else:
            w, n, widths, heights = load_data(index)

            print("\nSolving instance {} with {} model and {} solver:".format(
                index,
                self.__model.upper(),
                self.__solver
            ))
            print("---------------------------------------------------")
            print()
            
            try:
                (pos_x, pos_y, h, elapsed_time, rotations) = self.__solve(
                    w,
                    n,
                    widths,
                    heights
                )
                # optimal solution found
                if elapsed_time < 300:
                    print("Minimun Height Found: {}".format(h))
                    print("Solve Time: {}".format(elapsed_time))
                    print("--------------------------------")
                    print()
                # non optimal solution found
                else:
                    print("PROCESS TERMINATED, NON OPTIMAL SOLUTION FOUND:")
                    print("Minimun Height Found: {}".format(h))
                    print("--------------------------------")
                    print()

                if self.__print_img:
                    plot_device(
                        pos_x, pos_y,
                        widths, heights,
                        w, h, rotations,
                        self.__img_path + '/device-' + str(index) +'.png'
                )
            
            # no solution found within 5 mins
            except:
                print("PROCESS TERMINATED, NO SOLUTION FOUND")
                







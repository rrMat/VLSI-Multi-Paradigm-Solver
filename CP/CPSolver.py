##########################
# @lorenzoTribuiani
# Novembre 2022


import os
import time
import csv
from datetime import timedelta
from io import TextIOWrapper
from minizinc import Solver, Instance, Model
from utils.utils import plot_device, plot_device_rotation, load_data, write_sol

models={
    True: {
        "std": os.path.join(
            os.path.dirname(__file__),
            '../CP/src/solvers_rotation/MODEL_STD.mzn'
            ),
        "max": os.path.join(
            os.path.dirname(__file__),
            '../CP/src/solvers_rotation/MODEL_MAX.mzn'
        ),
        "sbs": os.path.join(
            os.path.dirname(__file__),
            '../CP/src/solvers_rotation/MODEL_SBS.mzn'
        )
    },
    False: {
        "std": os.path.join(
            os.path.dirname(__file__),
            '../CP/src/solvers/MODEL_STD.mzn'
            ),
        "max": os.path.join(
            os.path.dirname(__file__),
            '../CP/src/solvers/MODEL_MAX.mzn'
        ),
        "sbs": os.path.join(
            os.path.dirname(__file__),
            '../CP/src/solvers/MODEL_SBS.mzn'
        )
    }
}


class CPSolver:

    def __init__(self):
        pass

    def __solve(self, w: int, n: int, widths: list, heights: list, model_path: str, rotation: bool):

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
        model = Model(model_path)
        solver = Solver.lookup('chuffed')

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

        if rotation:
            rotations = out.solution.rotations
        else:
            rotations = []


        return (x_pos, y_pos, h, (end - start), rotations)



    def execute(self, file: TextIOWrapper, print_img: bool, ext: str, model_path: str, index: int, rotation: bool = False):

        """
        Execute the solving over a specific set of instances, prints data
        into a csv file and save the image

        Parameters
        ----------

        file: TextIOWrapper
            The output file csv
        print_img: bool
            Select wheter or not save the solution image
        ext: str
            Extension for img path
        model_path: str
            The path to the model
        index: int
            The indtances index (if 0 is selected all the instances will be executed)


        """

        dir_ = ext + "/rotation" if rotation else ext + "/no_rotation"
            
        if index == 0:
            header = ['device width', 'number of chips', "h", "solve time"]
            writer = csv.writer(file)
            writer.writerow(header)
            for i in range(1,41):

                w, n, widths, heights = load_data(i)
                (pos_x, pos_y, h, elapsed_time, rotations) = self.__solve(
                    w,
                    n,
                    widths,
                    heights,
                    model_path,
                    rotation
                )
            
                data = [w, n, h, elapsed_time]
                writer.writerow(data)
                
                write_sol(
                    os.path.join(
                        os.path.dirname(__file__),
                        "../CP/out/" + dir_ + "/solution-" + str(i) + ".txt"
                    ),
                    w,
                    h,
                    n,
                    widths,
                    heights,
                    pos_x,
                    pos_y
                )

                if print_img:
                    if rotation:
                        img_path = os.path.join(
                        os.path.dirname(__file__),
                        '../CP/img/' + ext + '/rotation/device-' + str(i) +'.png'
                        )
                        plot_device_rotation(pos_x, pos_y, widths, heights, w, h, rotations, img_path)
                    else:
                        img_path = os.path.join(
                            os.path.dirname(__file__),
                            '../CP/img/'+ ext +'/no_rotation/device-' + str(i) +'.png'
                        )
                        plot_device(pos_x, pos_y, widths, heights, w, h, img_path)

        else:

            w, n, widths, heights = load_data(index)
            (pos_x, pos_y, h, elapsed_time, rotations) = self.__solve(
                w,
                n,
                widths,
                heights,
                model_path,
                rotation
            )
            
            print("Minimun Height Found: {}".format(h))
            print("Solve Time: {}".format(elapsed_time))
            print("--------------------------------")
            print()

            if print_img:
                if rotation:
                    img_path = os.path.join(
                        os.path.dirname(__file__),
                    '   ../CP/img/' + ext +'/rotation/device-' + str(index) +'.png'
                    )
                    plot_device_rotation(pos_x, pos_y, widths, heights, w, h, rotations, img_path)
                else:
                    img_path = os.path.join(
                        os.path.dirname(__file__),
                        '../CP/img/' + ext +'no_rotation/device-' + str(index) +'.png'
                    )
                    plot_device(pos_x, pos_y, widths, heights, w, h, img_path)






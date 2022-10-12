from io import TextIOWrapper
import os
import time
import csv
from random import randint
from datetime import timedelta
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from minizinc import Solver, Instance, Model

model_std_path = os.path.join(
        os.path.dirname(__file__),
        'solvers/MODEL_STD.mzn'
    )

model_cum_path = os.path.join(
    os.path.dirname(__file__),
    'solvers/MODEL_CUM.mzn'
)

model_1s_path = os.path.join(
    os.path.dirname(__file__),
    'solvers/MODEL_1S.mzn'
) 

model_2s_path = os.path.join(
    os.path.dirname(__file__),
    'solvers/MODEL_2S.mzn'
)




def load_data(index: int):
    """
    Parse and load instances in order to be compatible with minizinc data type

    Parameters
    ----------

    index: int
        The instance number

    Returns
    -------

    w: int
        The plate width
    n: int
        The number of chips 
    widths: list
        the widths of the chips
    heights: list
        the heights of the chips

    """

    instance_path = os.path.join(
        os.path.dirname(__file__),
        '..\instances\ins-' + str(index) + '.txt')

    file = open(instance_path, 'r')
    lines = file.readlines()
    count = 0
    widths = []
    heights = []

    for line in lines:

        if count == 0:
            w = int(line)

        elif count == 1:
            n = int(line)

        else:
            chip_wh = line.split()
            widths.append(int(chip_wh[0]))
            heights.append(int(chip_wh[1]))            

        count += 1
    
    return w, n, widths, heights


def plot_device(pos_x: list, pos_y: list, widths: list, heights: list, w: int, h: int, img_path: str):  

    """
    Create and save an image of the solution produced

    Parameters
    ----------

    pos_x: list
        The x positions of the chips
    pos_y: list
        The y positions of the chips
    widths: list
        The chip's widths
    height: list
        The chip's height
    w: int
        The plate width
    h: int
        The plate height 
    img_path: str
        The path where the image will be saved

    """  

    fig, ax = plt.subplots()
    ax.axis([0, w, 0, h])
    for i in range(0, len(pos_x)):
        color = (randint(0,100)/100, randint(0,100)/100, randint(0,100)/100)
        rect = Rectangle(
            (pos_x[i], pos_y[i]),
            widths[i], heights[i],
            facecolor=color,
            edgecolor=(0,0,0),
            linewidth=2,
        )
        ax.add_patch(rect)
    plt.savefig(img_path)
    fig.clf()


def solve_2s(w:int, n:int, widths: list, heights: list, init_h: int):

    model = Model(model_2s_path)
    solver = Solver.lookup('chuffed')

    inst = Instance(solver, model)
    inst["w"] = w
    inst["n"] = n
    inst["widths"] =widths
    inst["heights"] = heights
    inst["h"] = init_h

    start = time.time()
    out = inst.solve(timeout=timedelta(seconds=300), free_search=True)
    end = time.time()

    if (end - start) >= 300:
        try:
            x_pos = out.solution.positions_x
            y_pos = out.solution.positions_y
            return x_pos, y_pos, init_h, (end - start)

        except:
            raise Exception()


    try:
        x_pos = out.solution.positions_x
        y_pos = out.solution.positions_y
        return x_pos, y_pos, init_h, (end - start)

    except:
        x_pos, y_pos, h, elapsed_time = solve_2s(w,n,widths, heights, init_h+1)
        return x_pos, y_pos, h, (end-start) + elapsed_time


def solve(w: int, n: int, widths: list, heights: list, model_path: str):

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

    return x_pos, y_pos, h, (end - start)


def execute(file: TextIOWrapper, print_img: bool, ext: str, model_path: str, index: int):

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
        
    if index == 0:
        header = ['device width', 'number of chips', "h", "solve time"]
        writer = csv.writer(file)
        writer.writerow(header)
        for i in range(1,41):

            w, n, widths, heights = load_data(i)
            pos_x, pos_y, h, elapsed_time = solve(
                w,
                n,
                widths,
                heights,
                model_path
            )
        
            data = [w, n, h, elapsed_time]
            writer.writerow(data)

            if print_img:
                img_path = os.path.join(
                    os.path.dirname(__file__),
                    'img/' + ext + '/device-' + str(i) +'.png'
                )
                plot_device(pos_x, pos_y, widths, heights, w, h, img_path)

    else:

        w, n, widths, heights = load_data(index)
        pos_x, pos_y, h, elapsed_time = solve(
            w,
            n,
            widths,
            heights,
            model_path
        )
        
        print("Minimun Height Found: {}".format(h))
        print("Solve Time: {}".format(elapsed_time))
        print()

        if print_img:
            img_path = os.path.join(
                os.path.dirname(__file__),
                'img/' + ext + '/device-' + str(index) +'.png'
            )
            plot_device(pos_x, pos_y, widths, heights, w, h, img_path)


def execute_2s(file: TextIOWrapper, print_img: bool, ext: str, index: int):

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
        
    if index == 0:
        header = ['device width', 'number of chips', "h", "solve time"]
        writer = csv.writer(file)
        writer.writerow(header)
        for i in range(1,41):

            w, n, widths, heights = load_data(i)

            ex_h = 0
            for i in range(0, len(widths)):
                ex_h += widths[i]*heights[i]

            ex_h//=w

            try:
                
                pos_x, pos_y, h, elapsed_time = solve_2s(
                    w,
                    n,
                    widths,
                    heights,
                    ex_h
                )
        
                data = [w, n, h, elapsed_time]
                writer.writerow(data)

                if print_img:
                    img_path = os.path.join(
                        os.path.dirname(__file__),
                        'img/' + ext + '/device-' + str(i) +'.png'
                    )
                    plot_device(pos_x, pos_y, widths, heights, w, h, img_path)

            except:
                print("No solution found in less then 5min for instance " + str(i))

    else:

        w, n, widths, heights = load_data(index)

        ex_h = 0
        for i in range(0, len(widths)):
            ex_h += widths[i]*heights[i]

        try:
            
            pos_x, pos_y, h, elapsed_time = solve_2s(
                w,
                n,
                widths,
                heights,
                ex_h
            )           
        
            print("Minimun Height Found: {}".format(h))
            print("Solve Time: {}".format(elapsed_time))
            print()

            if print_img:
                img_path = os.path.join(
                    os.path.dirname(__file__),
                    'img/' + ext + '/device-' + str(index) +'.png'
                )
                plot_device(pos_x, pos_y, widths, heights, w, h, img_path)
                
        except:
            print("No solution found in less then 5min for instance " + str(i))
            

def execute_all(index: int, print_img: bool=False):

    """
    Execute one or all the instaces over all the possible solvers, store the result in
    csv files and print the images

    Parameters
    ----------

    index: int
        the instances index (if 0 is selected all the instances are executed)
    print_img: bool
        Decide wheter or not the images are saved
    """    

    with open("CP/out/out_data_std.csv", "w", newline="") as file:
        execute(file, print_img, "STD_IMG", model_std_path, index)       

    with open("CP/out/out_data_chs.csv", "w", newline="") as file:
        execute(file, print_img, "CUM_IMG", model_cum_path, index)   

    with open("CP/out/out_data_1s.csv", "w", newline="") as file:
        execute(file, print_img, "1S_IMG", model_1s_path, index)

    with open("CP/out/out_data_2s.csv", "w", newline="") as file:
        execute_2s(file, print_img, "2S_IMG", index)
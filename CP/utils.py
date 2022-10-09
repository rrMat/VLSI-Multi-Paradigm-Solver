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
        'solvers/STANDARD.mzn'
    )

model_ch_path = os.path.join(
    os.path.dirname(__file__),
    'solvers/MODEL_CHS.mzn'
)

model_sb_path = os.path.join(
    os.path.dirname(__file__),
    'solvers/MODEL_SBS.mzn'
) 

def load_data(index):

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

def order_data(widths, heights):

    ordered = []
    for i in range(0, len(heights)):
        ordered.append((heights[i]*widths[i], i))

    ordered.sort(key=lambda tup: tup[0], reverse=True)

    ordered_widths = []
    ordered_heights = []
    
    for tup in ordered:

        ordered_widths.append(widths[tup[1]])
        ordered_heights.append(heights[tup[1]])

    return ordered_widths, ordered_heights



def plot_device(pos_x, pos_y, widths, heights, w, h, img_path):    

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


def solve(w, n, widths, heights, model_path):

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

    return x_pos, y_pos, w, h, widths, heights, (end - start)


def execute(file, print_img, ext, model_path, index):
        
    if index == 0:
        header = ['device width', 'number of chips', "h", "solve time"]
        writer = csv.writer(file)
        writer.writerow(header)
        for i in range(1,41):

            w, n, widths, heights = load_data(i)
            pos_x, pos_y, w, h, widths, heights, elapsed_time = solve(
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
        pos_x, pos_y, w, h, widths, heights, elapsed_time = solve(
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



def execute_all(index, print_img=False):    

    with open("CP/out/out_data.csv", "w", newline="") as file:
        execute(file, print_img, "STANDARD_IMG", model_std_path, index)       

    with open("CP/out/out_data_chs.csv", "w", newline="") as file:
        execute(file, print_img, "CHS_IMG", model_ch_path, index)   

    with open("CP/out/out_data_sbs.csv", "w", newline="") as file:
        execute(file, print_img, "SBS_IMG", model_sb_path, index)  
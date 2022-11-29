import os
from random import randint
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.legend_handler import HandlerTuple
from matplotlib.image import imread
import pandas as pd
import numpy as np

standard_colors = [
    "#E97777",
    "#90A17D",
    "#B1AFFF",
    "#F2D388"
]


# load data and convert it into readable types
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

    return w, n, np.array(widths), np.array(heights)


# plot the image for rotation
def plot_device(pos_x: list, pos_y: list, widths: list, heights: list, w: int, h: int, rotations: list, img_path="", override=True):
    """
    Create, save or show an image of the predicted plate when rotation is allowed

    Parameters
    ----------
    pos_x: list
        The x positions of the chips
    pos_y: list
        The y positions of the chips
    widths: list
        The chip's widths
    heights: list
        The chip's height
    w: int
        The plate width
    h: int
        The plate height
    rotations:
        An array of bool reporting the rotated chips
    img_path:
        The path where the image will be saved, if not specified the image will be shown but not saved.
        It can be string or Path.

    """
    if len(rotations) != 0:
        temp_w = [(widths[i] * (1-rotations[i])) + (heights[i]*rotations[i]) for i in range(0, len(widths))]
        temp_h = [(heights[i] * (1-rotations[i])) + (widths[i]*rotations[i]) for i in range(0, len(widths))]
        widths = temp_w
        heights = temp_h

    fig, ax = plt.subplots()
    ax.axis([0, w, 0, h])
    for i in range(0, len(widths)):
        color = (randint(0,100)/100, randint(0,100)/100, randint(0,100)/100)
        rect = Rectangle(
            (pos_x[i], pos_y[i]),
            widths[i], heights[i],
            facecolor=color,
            edgecolor=(0,0,0),
            linewidth=2,
        )
        ax.add_patch(rect)
    if img_path == "":
        plt.show()
    else:
        if (os.path.isfile(img_path) and override) or not os.path.isfile(img_path):
            plt.savefig(img_path)

    plt.close()


def write_sol(path, w: int, h: int, n: int, widths: list, heights: list, pos_x: list, pos_y: list, rotation: list):

    """
    Save solution in txt format in the format requested by the project description

    Parameters
    ----------
    :param path:
        The path where the output will be saved. Can be string or Path
    :param w: int
        The plate width
    :param h: int
        The plate height
    :param n: int
        The number of chips
    :param widths: list
        The chip's widths
    :param heights: list
        The chip's height
    :param pos_x: list
        The x positions of the chips
    :param pos_y: list
        The y positions of the chips
    :param rotation: list
        An array of bool reporting the rotated chips

    """

    with open(path, 'w') as f:
        f.write(f'{w} {int(h)}\n{n}\n')

        if len(rotation) != 0:
            for i in range(n):
                rotated = 'R' if rotation[i] else 'NR'

                f.write(f'{widths[i]} {heights[i]} {int(pos_x[i])} {int(pos_y[i])} {rotated}\n')

            f.close()
        else:
            for i in range(n):

                f.write(f'{widths[i]} {heights[i]} {int(pos_x[i])} {int(pos_y[i])} NR \n')

            f.close()

def load_sol(path):
    with open(path, 'r') as f:
        first_line = f.readline()
        if first_line == 'time exceeded':
            raise OSError()

        plate_width, plate_height = first_line.split(' ')
        n_chips = f.readline()

        plate_width = int(plate_width)
        plate_height = int(plate_height)
        n_chips = int(n_chips)

        chips_widths = []
        chips_heights = []
        pos_x = []
        pos_y = []
        rotated = []
        for i in range(n_chips):
            w, h, x, y, r = f.readline().split(' ')
            w = int(w)
            h = int(h)
            x = int(x)
            y = int(y)
            chips_widths.append(w)
            chips_heights.append(h)
            pos_x.append(x)
            pos_y.append(y)
            rotated.append(r)

    return plate_width, plate_height, n_chips, chips_widths, chips_heights, pos_x, pos_y


def write_stat_line(path, instance: int, height: int, time: float, solution_type: str):
    """
    Append to the csv file (or create it if file does not exist)
    the stats related to the solution of a specified instance

    :param path:
         The path where to append the stats. It can be string or Path.
    :param instance: int
        number of the solved instance
    :param height: int
        found height of the silicon plate
    :param time: float
        time spent to solve the instance
    :param solution_type: str
        Type of found solution\n
        - optimal\n
        - non-optimal\n
        - UNSAT\n
        - N/A 

    """
    print(path)
    if not os.path.exists(path):
        dataframe = pd.DataFrame(columns=['height', 'time', 'solution type'])
        dataframe.to_csv(path)

    dataframe = pd.read_csv(path, index_col=0)
    dataframe.loc[instance] = [height, time, solution_type]
    dataframe.to_csv(path)


def plot_bar_graph(datas,labels, colors=None, figsize=(10,15), saving_path=""):

    """
    Create a Bar plot of the given datas

    Parameters
    ----------

    datas: list
        A list containing the list of datas
    labels: list
        A list containing the list of labels
    color: list
        A list containing the colors of the bars, if not specified the standard set of color will be used
    figsize: tuple
       A tuple expressing the size of the chart. If not specified (10,15) will be used
    """

    fig, ax = plt.subplots(figsize=figsize)
    index = np.arange(1, len(datas[0])+1)
    width = 0.8/len(datas)
    ax.set_xticks(index)


    patches = []
    over5_colors = []


    for i in range(0,len(datas)):

        sel_col = colors[i] if colors != None else standard_colors[i]
        patch = Patch(color=sel_col, label=labels[i])
        patches.append(patch)
        color = [{p>=300: sel_col + "60", p<300: sel_col}[True] for p in datas[i]]
        ax.bar(index - (len(datas)//2-i)*width, datas[i],width, color=color)
        over5_colors.append(sel_col + "60")

    ax.set_yscale('log')

    over5_patches = [Patch(color=col, label="Over 5 min Execution") for col in over5_colors]
    labels.append("Over 5 min execution")
    patches.append(over5_patches)
    ax.grid(axis='y', which='both', color="#eeeeee")
    ax.set_axisbelow(True)
    plt.gca()
    plt.legend(handles=patches, labels=labels, handler_map = {list: HandlerTuple(None)})

    if saving_path != "":
        plt.savefig(saving_path)
    else:
        plt.show()


def display_img(paths, instances, figsize=(10,15)):
    cols = len(paths)
    rows = len(instances)

    fig, ax = plt.subplots(rows, cols, figsize=figsize)

    for ins_index in range(0, len(instances)):
        for index in range(0,len(paths)):
            ax[ins_index][index].imshow(imread(paths[index]+"device-" + str(instances[ins_index]) + ".png"))

    plt.show()


def load_stats(path):
    if not os.path.exists(path):
        return pd.DataFrame(columns=['height', 'height_lb', 'time'])
    return pd.read_csv(path, index_col = 0)


def display_times(path):
    dataframe = load_stats(path)
    plot_bar_graph([list(dataframe['time'])], ['Solved', 'Unsolved'], figsize=(10,5), y_lim=350)


def display_times_comparison(paths, model_names, number_of_instances):
    data = []
    for path in paths:
        dataframe = load_stats(path)
        data.append(dataframe['time'][:number_of_instances].tolist())
    plot_bar_graph(data, model_names, figsize=(10,5), y_lim=350)

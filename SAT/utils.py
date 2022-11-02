import os
from random import randint
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import csv
import numpy as np
import pandas as pd


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


# plot the images
def plot_device(pos_x: list, pos_y: list, widths: list, heights: list, w: int, h: int, img_path: str = ""):

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
        The path where the image will be saved, if not specified the image will be shown but not saved

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
    if img_path == "":
        plt.show()
    else:
        plt.savefig(img_path)

    fig.clf()


# plot the image for rotation
def plot_device_rotation(pos_x: list, pos_y: list, widths: list, heights: list, w:int, h: int, rotations: list, img_path: str = ""):

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
    height: list
        The chip's height
    w: int
        The plate width
    h: int
        The plate height
    rotations:
        An array of bool reporting the rotated chips
    img_path: str
        The path where the image will be saved, if not specified the image will be shown but not saved

    """

    actual_widths = [(widths[i] * (1-rotations[i])) + (heights[i]*rotations[i]) for i in range(0, len(widths))]
    actual_heights = [(heights[i] * (1-rotations[i])) + (widths[i]*rotations[i]) for i in range(0, len(widths))]

    plot_device(pos_x, pos_y, actual_widths, actual_heights, w, h, img_path)


def write_sol(path, w, h, n, widths, heights, pos_x, pos_y):

    """
    Save solution in txt format in the format requested by the project description

    Parameters
    ----------
    :param path: str
        The path where the output will be saved
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

    """

    with open(path, 'w') as f:
        f.write(f'{w} {int(h)}\n{n}\n')

        for i in range(n):
            f.write(f'{widths[i]} {heights[i]} {int(pos_x[i])} {int(pos_y[i])}\n')

        f.close()

def write_time_exceeded(path):
    with open(path, 'w') as f:
        f.write('time exceeded')
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
        for i in range(n_chips):
            w, h, x, y = f.readline().split(' ')
            w = int(w)
            h = int(h)
            x = int(x)
            y = int(y)
            chips_widths.append(w)
            chips_heights.append(h)
            pos_x.append(x)
            pos_y.append(y)

    return plate_width, plate_height, n_chips, chips_widths, chips_heights, pos_x, pos_y


def write_stat_line(path, instance, time):
    """
    Append to the csv file (or create it if file does not exist)
    the stats related to the solution of a specified instance

    :param path: str
         The path where to append the stats
    :param instance: int
        number of the solved instance
    :param height: int
        found height of the silicon plate
    :param time: float
        time spent to solve the instance

    """
    if not os.path.exists(path):
        dataframe = pd.DataFrame(columns=['time'])
        dataframe.to_csv(path)
    
    dataframe = pd.read_csv(path, index_col=0)
    dataframe.at[instance, 'time'] = time
    dataframe.to_csv(path)

def load_stats(path):
    return pd.read_csv(path)


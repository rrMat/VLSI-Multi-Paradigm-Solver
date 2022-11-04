import os
from random import randint
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

#load data and convert it into readable types
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

#plot the images
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

#plot the image for rotation
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

import os
from math import ceil
import pandas as pd
import time
def load_data(index: int, hs: list):
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
    start = time.time()
    total_area = 0
    for i in range(0, len(widths)):
        total_area += widths[i]*heights[i]

    min_h_a = total_area//w
    time_a = time.time() - start


    start = time.time()
    ratio = 0
    min_h_r = 0

    for i in range(0, len(widths)):
        ratio = widths[i]/w
        min_h_r +=ratio*heights[i]
    time_r = time.time() - start


    print("min_h_a: {}, min_h_r: {}, actual_h: {}, time_a: {}, time_r: {}".format(min_h_a, round(min_h_r), hs[index-1], time_a, time_r))


    return w, n, widths, heights

hs = pd.read_csv("CP/out/out_data_sbs.csv")['h'].to_list()

for i in range(1,41):
    load_data(i, hs)



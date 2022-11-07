from utils.utils import plot_bar_graph
import pandas as pd
import os

std_path = "CP/stats/no_rotation/out_data_std.csv"


std_data = pd.read_csv(std_path)

datas = [std_data["solve time"].to_list()]
labels=["std"]

plot_bar_graph(datas,labels)


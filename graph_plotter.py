from utils.utils import plot_bar_graph
import pandas as pd
import os

std_path = "CP/stats/no_rotation/out_data_std.csv"
max_path = "CP/stats/no_rotation/out_data_max.csv"
sbs_path = "CP/stats/no_rotation/out_data_sbs.csv"


std_data = pd.read_csv(std_path)
max_data = pd.read_csv(max_path)
sbs_data = pd.read_csv(sbs_path)

datas = [std_data["solve time"].to_list(), max_data["solve time"].to_list(), sbs_data["solve time"].to_list()]
labels=["std", "max", "sbs"]

plot_bar_graph(datas,labels)


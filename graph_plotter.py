from utils.utils import plot_bar_graph
import pandas as pd
import os

std_path = "CP/stats/rotation/out_data_std.csv"
cum_path = "CP/stats/rotation/out_data_max.csv"
#sbs_path = "CP/stats/rotation/out_data_sbs.csv"


std_data = pd.read_csv(std_path)
cum_data = pd.read_csv(cum_path)
#sbs_data = pd.read_csv(sbs_path)

datas = [std_data["solve time"].to_list(), cum_data["solve time"].to_list()]
labels=["std", "cum"]

plot_bar_graph(datas,labels,y_lim=1000)


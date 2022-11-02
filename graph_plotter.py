from utils.utils import plot_bar_graph
import pandas as pd
import os

std_path = os.path.join(
    os.path.dirname(__file__),
    "CP/stats/no_rotation/out_data_std.csv"
)

cum_path = os.path.join(
    os.path.dirname(__file__),
    "CP/stats/no_rotation/out_data_cum.csv"
)

sbs_path = os.path.join(
    os.path.dirname(__file__),
    "CP/stats/no_rotation/out_data_sbs.csv"
)

std_data = pd.read_csv(std_path)
cum_data = pd.read_csv(cum_path)
sbs_data = pd.read_csv(sbs_path)

datas = [std_data["solve time"].to_list(), cum_data["solve time"].to_list(), sbs_data["solve time"].to_list()]
colors = ["red", "green", "blue"]
labels=["std", "cum", "sbs"]

plot_bar_graph(datas,labels,y_lim=10)


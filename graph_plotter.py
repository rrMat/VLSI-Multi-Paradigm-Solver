from utils.utils import plot_bar_graph, display_img
import pandas as pd
import numpy as np

std_path = "CP/stats/rotation/out_data_std.csv"
max_path = "CP/stats/rotation/out_data_max.csv"
sbs_path = "CP/stats/rotation/out_data_sbs.csv"

std_img = "CP/img/STD/no_rotation/"
max_img = "CP/img/MAX/no_rotation/"
sbs_img = "CP/img/SBS/no_rotation/"

imgs_paths = [std_img, max_img, sbs_img]

display_img(imgs_paths, [1,10,20, 30])


std_data = pd.read_csv(std_path)
max_data = pd.read_csv(max_path)
sbs_data = pd.read_csv(sbs_path)

std = np.array(std_data["solve time"].to_list())
max = np.array(max_data["solve time"].to_list())
sbs = np.array(sbs_data["solve time"].to_list())


datas = [std, max, sbs]
labels=["std", "max", "sbs"]

plot_bar_graph(datas,labels)

mean_std = sum(std)/len(std)
mean_max = sum(max)/len(max)
mean_sbs = sum(sbs)/len(sbs)

over5_std = len(std[std >= 300])
over5_max = len(max[max >= 300])
over5_sbs = len(sbs[sbs >= 300])

print("std: {}, {}".format(mean_std, over5_std))
print("max: {}, {}".format(mean_max, over5_max))
print("sbs: {}, {}".format(mean_sbs, over5_sbs))


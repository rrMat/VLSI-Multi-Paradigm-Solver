from utils.utils import write_experimental_result, plot_bar_graph
import pandas as pd


base_ref_CNR = "CP/stats/no_rotation/chuffed/"
base_ref_GNR = "CP/stats/no_rotation/gecode/"
base_ref_ORNR = "CP/stats/no_rotation/or-tools/"

base_ref_CR = "CP/stats/rotation/chuffed/"
base_ref_GR = "CP/stats/rotation/gecode/"
base_ref_ORR = "CP/stats/rotation/or-tools/"

STD_CHUFFED_NR = base_ref_CR + "out_data_std.csv"
CML_CHUFFED_NR = base_ref_CR + "out_data_cml.csv"
SYB_CHUFFED_NR = base_ref_CR + "out_data_syb.csv"

STD_GECODE_NR = base_ref_GR + "out_data_std.csv"
CML_GECODE_NR = base_ref_GR + "out_data_cml.csv"
SYB_GECODE_NR = base_ref_GR + "out_data_syb.csv"

STD_ORTOOLS_NR = base_ref_ORR + "out_data_std.csv"
CML_ORTOOLS_NR = base_ref_ORR + "out_data_cml.csv"
SYB_ORTOOLS_NR = base_ref_ORR + "out_data_syb.csv"

std_c_nr = pd.read_csv(STD_CHUFFED_NR)["time"]
cml_c_nr = pd.read_csv(CML_CHUFFED_NR)["time"]
syb_c_nr = pd.read_csv(SYB_CHUFFED_NR)["time"]

std_g_nr = pd.read_csv(STD_GECODE_NR)["time"]
cml_g_nr = pd.read_csv(CML_GECODE_NR)["time"]
syb_g_nr = pd.read_csv(SYB_GECODE_NR)["time"]

std_o_nr = pd.read_csv(STD_ORTOOLS_NR)["time"]
cml_o_nr = pd.read_csv(CML_ORTOOLS_NR)["time"]
syb_o_nr = pd.read_csv(SYB_ORTOOLS_NR)["time"]

plot_bar_graph(
    [std_o_nr, cml_o_nr, syb_o_nr], 
    ["STD or-tools rotation", "CML or-tools rotation", "SYB or-tools rotation"])


# write_experimental_result(
#      "CP/stats/total_stats_rotation.csv",
#      [
#          STD_CHUFFED_NR,
#          CML_CHUFFED_NR,
#          SYB_CHUFFED_NR,
#          STD_GECODE_NR,
#          CML_GECODE_NR,
#          SYB_GECODE_NR,
#          STD_ORTOOLS_NR,
#          CML_ORTOOLS_NR,
#          SYB_ORTOOLS_NR
#      ],
#      [
#          "STD Chuffed",
#          "CML Chuffed",
#          "SYB Chuffed",
#          "STD Gecode",
#          "CML Gecode",
#          "SYB Gecode",
#          "STD Or-T.",
#          "CML Or-T.",
#          "SYB Or-T.",
#      ])


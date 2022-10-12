from email import utils
import argparse
import utils


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("instance", type=int, help="The instance's number to execute (1-40). Type 0 to execute all the instances")
    parser.add_argument("-all", "--execute_all", action='store_true', help="Execute on all possible solvers")
    parser.add_argument("-std", "--standard_solver", action='store_true', help='select standard solver for execution')
    parser.add_argument("-cum", "--cumulative_con_solver", action='store_true', help='select cumulative constraint solver for execution')
    parser.add_argument("-1s", "--single_simmetry_solver", action='store_true', help='select single simmetry breaking solver for execution')
    parser.add_argument("-2s", "--double_simmetry_solver", action='store_true', help='select double simmetry breaking solver for execution')
    parser.add_argument("-p", "--print_img", action='store_true', help="Print image representation of solution")
    args = parser.parse_args()

    if args.execute_all:
        utils.execute_all(args.instance, args.print_img)
    else:

        mode = 'w' if args.instance == 0 else 'a'

        if args.simmetry_breaking_solver:
            with open("CP/out/out_data_sbs.csv", mode, newline="") as file:
                utils.execute(file, args.print_img, "1S_IMG", utils.model_1s_path, args.instance)
           
        if args.cumulative_height_solver:
            with open("CP/out/out_data_chs.csv", mode, newline="") as file:
                utils.execute(file, args.print_img, "CUM_IMG", utils.model_cum_path, args.instance)

        if args.standard_solver:
            with open("CP/out/out_data_std.csv", mode, newline="") as file:
                utils.execute(file, args.print_img, "STD_IMG", utils.model_std_path, args.instance)

        if args.fixed_height_solver:
            with open("CP/out/out_data_fixh.csv", mode, newline="") as file:
                utils.execute_fix_h(file, args.print_img, "2S_IMG", args.instance)


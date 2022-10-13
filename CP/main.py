import argparse
import  utils

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("instance", type=int, help="The instance's number to execute (1-40). Type 0 to execute all the instances")
    parser.add_argument("-all", "--execute_all", action='store_true', help="Execute on all possible solvers")
    parser.add_argument("-std", "--standard_solver", action='store_true', help='select standard solver for execution')
    parser.add_argument("-max", "--maximum_wh_solver", action='store_true', help='select boundary check solver for execution')
    parser.add_argument("-sbs", "--simmetry_breaking_solver", action='store_true', help='select simmetry breaking solver for execution')
    parser.add_argument("-p", "--print_img", action='store_true', help="Print image representation of solution")
    args = parser.parse_args()

    if args.execute_all:
        utils.execute_all(args.instance, args.print_img)
    else:

        mode = 'w' if args.instance == 0 else 'a'

        if args.simmetry_breaking_solver:
            with open("CP/out/out_data_sbs.csv", mode, newline="") as file:
                utils.execute(file, args.print_img, "SBS_IMG", utils.model_sbs_path, args.instance)
           
        if args.maximum_wh_solver:
            with open("CP/out/out_data_max.csv", mode, newline="") as file:
                utils.execute(file, args.print_img, "MAX_IMG", utils.model_max_path, args.instance)

        if args.standard_solver:
            with open("CP/out/out_data_std.csv", mode, newline="") as file:
                utils.execute(file, args.print_img, "STD_IMG", utils.model_std_path, args.instance)



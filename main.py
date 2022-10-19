import argparse
import utils.CP as CP

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("Paradigm", type=str, help="Select the solving paradigm. Allowed values: CP | SAT | SMT | LP")
    parser.add_argument("instance", type=int, help="The instance's number to execute (1-40). Type 0 to execute all the instances")
    parser.add_argument("-all", "--execute_all", action='store_true', help="Execute on all possible solvers")
    parser.add_argument("-p", "--print_img", action='store_true', help="Print image representation of solution")
    parser.add_argument("-std", "--standard_solver", action='store_true', help='select standard solver for execution')
    parser.add_argument("-max", "--maximum_wh_solver", action='store_true', help='select boundary check solver for execution')
    parser.add_argument("-sbs", "--simmetry_breaking_solver", action='store_true', help='select simmetry breaking solver for execution')
    parser.add_argument("-r", "--rotation_allowed", action='store_true', help="Allow rotation of chips in solving")
    args = parser.parse_args()

    if args.Paradigm == "CP":
        if args.execute_all:
            CP.execute_all(args.instance, args.rotation_allowed, args.print_img)

        else:
            mode = 'w' if args.instance == 0 else 'a'
            out_folder = "out_rotation" if args.rotation_allowed else "out" 

            if args.simmetry_breaking_solver:
                with open("CP/" + out_folder + "/out_data_sbs.csv", mode, newline="") as file:
                    CP.execute(file, args.print_img, "SBS_IMG", CP.models[args.rotation_allowed]["sbs"], args.instance, args.rotation_allowed)
           
            if args.maximum_wh_solver:
                with open("CP/" + out_folder + "/out_data_max.csv", mode, newline="") as file:
                    CP.execute(file, args.print_img, "MAX_IMG", CP.models[args.rotation_allowed]["max"], args.instance, args.rotation_allowed)

            if args.standard_solver:
                with open("CP/" + out_folder + "/out_data_std.csv", mode, newline="") as file:
                    CP.execute(file, args.print_img, "STD_IMG", CP.models[args.rotation_allowed]["std"], args.instance, args.rotation_allowed)

    
    elif args.Paradigm == "SAT":
        pass

    elif args.Paradigm == "SMT":
        pass

    elif args.Paradigm == "LP":
        pass



import argparse
from CP.CPSolver import CPSolver, models

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

        solver = CPSolver()
        out_folder = "stats/rotation" if args.rotation_allowed else "stats/no_rotation"

        if args.execute_all:            

            solver.execute(args.print_img, "STD/", "std", args.instance, args.rotation_allowed)
            solver.execute(args.print_img, "MAX/", "max", args.instance, args.rotation_allowed)
            solver.execute(args.print_img, "SBS/", "sbs", args.instance, args.rotation_allowed)

        else:
            if args.standard_solver:
                solver.execute(args.print_img, "STD/", "std", args.instance, args.rotation_allowed)
            if args.simmetry_breaking_solver:
                solver.execute(args.print_img, "SBS/", "sbs", args.instance, args.rotation_allowed)           
            if args.maximum_wh_solver:
                solver.execute(args.print_img, "MAX/", "max", args.instance, args.rotation_allowed)
                
           

    elif args.Paradigm == "SAT":
        pass

    elif args.Paradigm == "SMT":
        pass

    elif args.Paradigm == "LP":
        pass



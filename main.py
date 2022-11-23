import argparse
from CP.src.CPSolver import CPSolver

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog="VLSI multi paradigm Solver",
        epilog="See '<command> --help' to read about a specific sub-command."
    )
    
    base_parser = argparse.ArgumentParser(add_help=False)
    #Optinal shared arguments
    base_parser.add_argument("-ins", "--instance", type=int, help="The instance's number to execute (1-40). Omit to execute all the instances")
    base_parser.add_argument("-p", "--print_img", action='store_true', help="Print image representation of solution")
    base_parser.add_argument("-r", "--rotation", action='store_true', help="Allow rotation of chips in solving")
    
    #parsers for instance
    parsers = parser.add_subparsers(dest="Paradigm")
    CP_parser = parsers.add_parser("CP", parents=[base_parser])
    SAT_parser = parsers.add_parser("SAT", parents=[base_parser])
    SMT_parser = parsers.add_parser("SMT", parents=[base_parser])
    LP_parser = parsers.add_parser("LP", parents=[base_parser])

    #CP parameters (required)
    CP_parser.add_argument("-m", "--model", required=True, nargs='+', type=str, choices=["max", "sbs"], help='select models. \nAcceptable values: max | sbs')
    CP_parser.add_argument("-s", "--solver", required=True, nargs='+', type=str, choices=["chuffed", "gecode", "or-tools"],  help='select solver. \nAcceptable values: chugged | gecode')
    
    
    args = parser.parse_args()

    if args.Paradigm == "CP" :
        for model in args.model:
            for solver in args.solver:
                cp = CPSolver(
                    model,
                    solver,
                    args.rotation,
                    args.print_img
                )
                cp.execute(args.instance)                   

    elif args.Paradigm == "SAT":
        pass

    elif args.Paradigm == "SMT":
        pass

    elif args.Paradigm == "LP":
        pass



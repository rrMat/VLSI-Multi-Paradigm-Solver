import argparse
from CP.src.CPSolver import CPSolver
from SAT.src.SATSolver import SATSolver
from MIP.src.mip import MIP

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
    MIP_parser = parsers.add_parser("MIP", parents=[base_parser])

    #CP parameters (required)
    CP_parser.add_argument("-m", "--model", required=True, nargs='+', type=str, choices=["max", "sbs"], help='select models. \nAcceptable values: max | sbs')
    CP_parser.add_argument("-s", "--solver", required=True, nargs='+', type=str, choices=["chuffed", "gecode", "or-tools"],  help='select solver. \nAcceptable values: chugged | gecode')

    # MIP arguments
    MIP_parser.add_argument('-m', '--model', required=True, nargs='+', type=str,
                            choices=['std'],
                            help='Select MIP model.\n'
                                 'Possible models: std | cplex | copt | highs | xpress | cbc')
    MIP_parser.add_argument('-s', '--solver', required=True, nargs='+', type=str,
                            choices=['gurobi', 'cplex', 'copt', 'highs', 'xpress', 'cbc'],
                            help='Select one or more solvers for MIP formulation.\n'
                                 'Possible solvers: gurobi | cplex | copt | highs | xpress | cbc')
    MIP_parser.add_argument('-a', '--ampl_dir', required=False, default=None, type=str,
                            help='If the AMPL installation directory is not in the system search path '
                                 'you need to specify the full path to the AMPL installation directory.')

    args = parser.parse_args()

    if args.Paradigm == "CP":
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
        OUT_DIRECTORY_RELATIVE_PATH = '/out/'
        IMG_DIRECTORY_RELATIVE_PATH = '/img/'
        STATS_RELATIVE_PATH = '/stats/'

        #SAT_solver = SAT(args.instance,
        #                 args.model,
        #                 args.rotation_allowed,
        #                 args.symmetry_required,
        #                 args.encoding_type,
        #                 args.number_of_instances,
        #                 args.time_available,
        #                 args.interrupt,
        #                 args.verbose,
        #                 args.override,
        #                 OUT_DIRECTORY_RELATIVE_PATH,
        #                 IMG_DIRECTORY_RELATIVE_PATH,
        #                 STATS_RELATIVE_PATH)

        for encoder in ['seq', 'np', 'bw', 'he']:
            SATSolver('SATModel', rotation_allowed = True,
                            symmetry_required=False,
                            encoding_type=encoder,
                            number_of_instances=40,
                            time_available=300,
                            interrupt=True,
                            verbose=True,
                            out_directory_path = 'SAT' + OUT_DIRECTORY_RELATIVE_PATH,
                            img_directory_path = 'SAT' + IMG_DIRECTORY_RELATIVE_PATH,
                            stats_directory_path = 'SAT' + STATS_RELATIVE_PATH,
                            OVERRIDE = True
                ).execute()

        for rotation in [True, False]:
            for symmetry_required in [True, False]:
                SATSolver('SATModel', rotation_allowed = rotation,
                                symmetry_required=symmetry_required,
                                encoding_type='bw',
                                number_of_instances=40,
                                time_available=300,
                                interrupt=True,
                                verbose=True,
                                out_directory_path = 'SAT' + OUT_DIRECTORY_RELATIVE_PATH,
                                img_directory_path = 'SAT' + IMG_DIRECTORY_RELATIVE_PATH,
                                stats_directory_path = 'SAT' + STATS_RELATIVE_PATH,
                                OVERRIDE = False
                ).execute()


    elif args.Paradigm == "SMT":
        pass

    elif args.Paradigm == "MIP":
        mip = MIP(ampl_dir=args.ampl_dir, rotation=args.rotation, print_image=args.print_img)

        for model in args.model:
            mip.set_model(model)
            for solver in args.solver:
                mip.set_solver(solver)
                mip.execute(args.instance)



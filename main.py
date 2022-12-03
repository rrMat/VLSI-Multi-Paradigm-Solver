import argparse
from CP.src.CPSolver import CPSolver
from SAT.src.SATSolver import SATSolver
from MIP.src.mip import MIP
from SMT.src.SMTSolver import SMTSolver
import os
import utils.utils as utils
import copy


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog="VLSI multi paradigm Solver",
        epilog="See '<command> --help' to read about a specific sub-command."
    )

    base_parser = argparse.ArgumentParser(add_help=False)
    #Optinal shared arguments
    base_parser.add_argument("-i", "--instance", type=int, help="The instance's number to execute (1-40). Omit to execute all the instances")
    base_parser.add_argument("-p", "--print_img", action='store_true', help="Print image representation of solution")
    base_parser.add_argument("-r", "--rotation", action='store_true', help="Allow rotation of chips in solving")

    #parsers for instance
    parsers = parser.add_subparsers(dest="Paradigm")
    CP_parser = parsers.add_parser("CP", parents=[base_parser])
    SAT_parser = parsers.add_parser("SAT", parents=[base_parser])
    SMT_parser = parsers.add_parser("SMT", parents=[base_parser])
    MIP_parser = parsers.add_parser("MIP", parents=[base_parser])

    #CP parameters (required)
    CP_parser.add_argument("-m", "--model", required=True, nargs='+', type=str,
                           choices=CPSolver.acceptable_models,
                           help='select models. \nAcceptable values: max | sbs')
    CP_parser.add_argument("-s", "--solver", required=True, nargs='+', type=str,
                           choices=CPSolver.acceptable_solvers,
                           help='select solver. \nAcceptable values: chugged | gecode')

    # MIP arguments
    MIP_parser.add_argument('-m', '--model', required=True, nargs='+', type=str,
                            choices=['std', 'strong'],
                            help='Select MIP model.\n'
                                 'Possible models: std | strong')
    MIP_parser.add_argument('-s', '--solver', required=True, nargs='+', type=str,
                            choices=['gurobi', 'cplex', 'copt', 'highs', 'xpress'],
                            help='Select one or more solvers for MIP formulation.\n'
                                 'Possible solvers: gurobi | cplex | copt | highs | xpress')
    MIP_parser.add_argument('-a', '--ampl_dir', required=False, default=None, type=str,
                            help='If the AMPL installation directory is not in the system search path '
                                 'you need to specify the full path to the AMPL installation directory.')

    # SAT arguments 
    SAT_parser.add_argument('-m', '--model', required=True, type=str, 
                            choices=['SATModel', 'SATModelBorders'],
                            help='Select SAT model.\n'
                                 'Possible models: SATModel | SATModelBorders')
    SAT_parser.add_argument('-e', '--encoding', default='bw', type=str, 
                            choices=['seq','np','bw','he'],
                            help='Select SAT encoding.\n'
                                 'Possible models: seq | np | bw | he')
    SAT_parser.add_argument('-sb', '--symmetry_breaking', default=True, type=bool,
                            help='Choose if the symmetry breaking constraint has to be used\n')
    SAT_parser.add_argument('-t', '--time_available', default=300, type=int, 
                            help='Define the time available to solve an instance\n')
    SAT_parser.add_argument('-o', '--override', default=True, type=bool,
                            help='Choose if the results have to be override\n')
    SAT_parser.add_argument('-v', '--verbose', default=False, type=bool,
                            help='Print results of execution\n')
    SAT_parser.add_argument('-n', '--number_of_instances', default=40, type=int,
                            help='Number of instances to execute\n')

    # SMT arguments 
    SMT_parser.add_argument('-m', '--model', required=True, type=str, 
                            choices=['z3Py', 'z3Py_rotation', 'z3Py_parallel_rotation', 
                            'z3Py_parallel', 'pySMT_z3', 'pySMT_msat', 'analysis'],
                            help='Select SMT model.\n'
                                 'Possible models: z3Py')

    args = parser.parse_args()

    if args.Paradigm == "CP" :

        cp = CPSolver(rotation=args.rotation,
                      print_img = args.print_img)

        for model in args.model:
            for solver in args.solver:
                cp.update_model(model)
                cp.update_solver(solver)
                cp.execute(args.instance)

        # Proposta: mettere questo dentro un metodo di CPSolver chiamato execute(). In questo modo 
        # l'unica cosa che facciamo nel main è chiamare l'execute() di un certo Solver con certe caratteristiche.

    elif args.Paradigm == "SAT":
        SATSolver(model_name = args.model,
                  rotation_allowed = args.rotation,
                  symmetry_required = args.symmetry_breaking,
                  encoding_type = args.encoding,
                  number_of_instances=args.number_of_instances,
                  time_available=args.time_available,
                  verbose=args.verbose,
                  OVERRIDE = args.override).execute()
        
    elif args.Paradigm == "SMT":
        SMTSolver(model_name = args.model).execute()
        
    elif args.Paradigm == "MIP":
        mip = MIP(ampl_dir=args.ampl_dir, 
                  rotation=args.rotation, 
                  print_image=args.print_img)

        
        # Proposta: mettere questo dentro un metodo di MIP chiamato execute(). In questo modo 
        # l'unica cosa che facciamo nel main è chiamare l'execute() di un certo Solver con certe caratteristiche.

        for solver in args.solver:
            mip.set_solver(solver)
            for model in args.model:
                mip.set_model(model)
                mip.execute(args.instance)



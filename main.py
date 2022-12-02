import argparse
from CP.src.CPSolver import CPSolver
from SAT.src.SATSolver import SATSolver
from MIP.src.mip import MIP
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
                                 'Possible models: std | cplex | copt | highs | xpress | cbc')
    MIP_parser.add_argument('-s', '--solver', required=True, nargs='+', type=str,
                            choices=['gurobi', 'cplex', 'copt', 'highs', 'xpress', 'cbc'],
                            help='Select one or more solvers for MIP formulation.\n'
                                 'Possible solvers: gurobi | cplex | copt | highs | xpress | cbc')
    MIP_parser.add_argument('-a', '--ampl_dir', required=False, default=None, type=str,
                            help='If the AMPL installation directory is not in the system search path '
                                 'you need to specify the full path to the AMPL installation directory.')

    args = parser.parse_args()

    if args.Paradigm == "CP" :

        cp = CPSolver(
            rotation=args.rotation,
            print_img = args.print_img
        )

        for model in args.model:
            for solver in args.solver:
                cp.update_model(model)
                cp.update_solver(solver)
                cp.execute(args.instance)                   

    elif args.Paradigm == "SAT":

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

        MODEL_NAMES = ['SATModel', 'SATModelBorders']
        ENCODERS_NAMES = ['seq', 'np', 'bw', 'he']
        
        NUMBER_OF_INSTANCES = 20
        TIME_AVAILABLE = 300
        INTERRUPT = True
        BEST_ENCODER = 'bw'
        VERBOSE = False
        BEST_MODEL = 'SATModel'

        OVERRIDE = False


        # Create the directory which should contains the analysis results
        os.makedirs('SAT/analysis', exist_ok=True)
        
        # Comparison of all the encoding approaches
        print('Comparison of the encodings...')
        csv_paths_encodings = []
        names = []
        for encoder in ENCODERS_NAMES:
            csv_path = SATSolver('SATModel', 
                                rotation_allowed = False,
                                symmetry_required = False,
                                encoding_type = encoder,
                                number_of_instances = NUMBER_OF_INSTANCES,
                                time_available = TIME_AVAILABLE,
                                interrupt = INTERRUPT,
                                verbose = VERBOSE,
                                solver = 'z3',
                                OVERRIDE = True).execute()
            csv_paths_encodings.append(csv_path)
            names.append('SATModel' + ''.join(['_'+ letter for letter in encoder]))
        utils.display_times_comparison(csv_paths_encodings, copy.deepcopy(names), NUMBER_OF_INSTANCES, 'SAT/analysis/encodingComparison.png')
        utils.write_experimental_result('SAT/analysis/encodingComparison.csv', csv_paths_encodings, names)
        print(names)
        # Comparison of the models 
        print('[WITHOUT ROTATION] Comparison of the models with symmetry and without...')
        csv_paths_models_withoutRotation = []
        names = []
        for model_name in MODEL_NAMES:
            for symmetry_required in [False, True]:
                csv_path = SATSolver(model_name = model_name, 
                                    rotation_allowed = False,
                                    symmetry_required = symmetry_required,
                                    encoding_type = BEST_ENCODER,
                                    number_of_instances=NUMBER_OF_INSTANCES,
                                    time_available=TIME_AVAILABLE,
                                    interrupt=INTERRUPT,
                                    verbose=VERBOSE,
                                    solver='z3',
                                    OVERRIDE = OVERRIDE).execute()
                csv_paths_models_withoutRotation.append(csv_path)
                names.append(model_name + ''.join(['_'+ letter for letter in BEST_ENCODER]) + ('+ sb' if symmetry_required else ''))
        utils.display_times_comparison(csv_paths_models_withoutRotation, copy.deepcopy(names), NUMBER_OF_INSTANCES, 'SAT/analysis/modelsComparison_withoutRotation.png')
        utils.write_experimental_result('SAT/analysis/modelsComparison_withoutRotation.csv', csv_paths_models_withoutRotation, names)

        # Comparison of the models 
        print('[WITH ROTATION] Comparison of the models with symmetry and without...')
        csv_paths_models_withRotation = []
        names = []
        for model_name in MODEL_NAMES:
            for symmetry_required in [True, False]:
                csv_path = SATSolver(model_name = model_name, 
                                    rotation_allowed = True,
                                    symmetry_required = symmetry_required,
                                    encoding_type = BEST_ENCODER,
                                    number_of_instances = NUMBER_OF_INSTANCES,
                                    time_available = TIME_AVAILABLE,
                                    interrupt = INTERRUPT,
                                    verbose = VERBOSE,
                                    solver = 'z3',
                                    OVERRIDE = OVERRIDE).execute()
                csv_paths_models_withRotation.append(csv_path)
                names.append(model_name + ''.join(['_'+ letter for letter in BEST_ENCODER]) + ('+ sb' if symmetry_required else ''))
        utils.display_times_comparison(csv_paths_models_withRotation, copy.deepcopy(names), NUMBER_OF_INSTANCES, 'SAT/analysis/modelsComparison_withRotation.png')
        utils.write_experimental_result('SAT/analysis/modelsComparison_withRotation.csv', csv_paths_models_withRotation, names)
        

        for model_name in ['SATModel', 'SATModelBorders']:
            for rotation in [True, False]:
                for symmetry_required in [True, False]:
                    for encoder in ['bw']:
                        SATSolver(model_name = model_name, 
                                  rotation_allowed = rotation,
                                  symmetry_required = symmetry_required,
                                  encoding_type = encoder,
                                  number_of_instances=NUMBER_OF_INSTANCES,
                                  time_available=TIME_AVAILABLE,
                                  interrupt=INTERRUPT,
                                  verbose=VERBOSE,
                                  solver='z3',
                                  OVERRIDE = OVERRIDE).execute()

    elif args.Paradigm == "SMT":
        pass

    elif args.Paradigm == "MIP":
        mip = MIP(ampl_dir=args.ampl_dir, rotation=args.rotation, print_image=args.print_img)

        for solver in args.solver:
            mip.set_solver(solver)
            for model in args.model:
                mip.set_model(model)
                mip.execute(args.instance)



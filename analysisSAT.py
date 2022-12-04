import argparse
from SAT.src.SATSolver import SATSolver
import os
import utils.utils as utils
import copy


if __name__ == '__main__':
    MODEL_NAMES = ['SATModel', 'SATModelBorders']
    ENCODERS_NAMES = ['seq', 'np', 'bw', 'he']

    NUMBER_OF_INSTANCES_TO_COMPUTE = 25
    NUMBER_OF_INSTANCES_TO_PRINT = 40
    TIME_AVAILABLE = 300
    INTERRUPT = True
    BEST_ENCODER = 'bw'
    VERBOSE = True
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
                            number_of_instances = NUMBER_OF_INSTANCES_TO_COMPUTE,
                            time_available = TIME_AVAILABLE,
                            verbose = VERBOSE,
                            OVERRIDE = OVERRIDE).execute()
        csv_paths_encodings.append(csv_path)
        names.append('SATModel' + ''.join(['_'+ letter for letter in encoder]))
    utils.display_times_comparison(csv_paths_encodings, copy.deepcopy(names), NUMBER_OF_INSTANCES_TO_PRINT, 'SAT/analysis/encodingComparison.png')
    utils.write_experimental_result('SAT/analysis/encodingComparison.csv', csv_paths_encodings, names)
    
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
                                number_of_instances=NUMBER_OF_INSTANCES_TO_COMPUTE,
                                time_available=TIME_AVAILABLE,
                                verbose=VERBOSE,
                                OVERRIDE = OVERRIDE).execute()
            csv_paths_models_withoutRotation.append(csv_path)
            names.append(model_name + ''.join(['_'+ letter for letter in BEST_ENCODER]) + ('+ sb' if symmetry_required else ''))
    utils.display_times_comparison(csv_paths_models_withoutRotation, copy.deepcopy(names), NUMBER_OF_INSTANCES_TO_PRINT, 'SAT/analysis/modelsComparison_withoutRotation.png')
    utils.write_experimental_result('SAT/analysis/modelsComparison_withoutRotation.csv', csv_paths_models_withoutRotation, names)

    # Comparison of the models
    print('[WITH ROTATION] Comparison of the models with symmetry and without...')
    csv_paths_models_withRotation = []
    names = []
    for model_name in MODEL_NAMES:
        for symmetry_required in [False, True]:
            csv_path = SATSolver(model_name = model_name, 
                                rotation_allowed = True,
                                symmetry_required = symmetry_required,
                                encoding_type = BEST_ENCODER,
                                number_of_instances = NUMBER_OF_INSTANCES_TO_COMPUTE,
                                time_available = TIME_AVAILABLE,
                                verbose = VERBOSE,
                                OVERRIDE = OVERRIDE).execute()
            csv_paths_models_withRotation.append(csv_path)
            names.append(model_name + ''.join(['_'+ letter for letter in BEST_ENCODER]) + ('+ sb' if symmetry_required else ''))
    utils.display_times_comparison(csv_paths_models_withRotation, copy.deepcopy(names), NUMBER_OF_INSTANCES_TO_PRINT, 'SAT/analysis/modelsComparison_withRotation.png')
    utils.write_experimental_result('SAT/analysis/modelsComparison_withRotation.csv', csv_paths_models_withRotation, names)
    

    for model_name in ['SATModel', 'SATModelBorders']:
        for rotation in [True, False]:
            for symmetry_required in [True, False]:
                for encoder in ['bw']:
                    SATSolver(model_name = model_name,
                                rotation_allowed = rotation,
                                symmetry_required = symmetry_required,
                                encoding_type = encoder,
                                number_of_instances=NUMBER_OF_INSTANCES_TO_COMPUTE,
                                time_available=TIME_AVAILABLE,
                                verbose=VERBOSE,
                                OVERRIDE = OVERRIDE).execute()


from z3 import *
import math
import numpy as np 
import time
import utils.utils as utils
import multiprocessing
import os
from SAT.src.SATModel import SATModel
from SAT.src.SATModelBorders import SATModelBorders
import SAT.src.sat_utils as sat_utils

class SATSolver:

    MODEL_names = {
        'SATModel': SATModel,
        'SATModelBorders': SATModelBorders,
    }

    TIME_AVAILABLE = 300
    NUMBER_OF_INSTANCES = 40

    def __init__(self, model_name, rotation_allowed, symmetry_required, encoding_type, 
                       instance, print_img, verbose):
        
        self.model_name = model_name
        self.rotation_allowed = rotation_allowed
        self.symmetry_required = symmetry_required
        self.encoding_type = encoding_type
        self.instances = range(1, self.NUMBER_OF_INSTANCES + 1) if instance is None else [instance]
        self.verbose = verbose
        self.print_img = print_img
        self.interrupt = False if self.TIME_AVAILABLE == 0 else True
        self.OVERRIDE = True

        # Define the result label
        self.LABEL = self.model_name
        self.LABEL = self.LABEL + '/' + ('rotation' if self.rotation_allowed else 'no_rotation') 
        self.LABEL = self.LABEL + '/' + ('symmetry_required' if self.symmetry_required else 'no_symmetry_required')
        self.LABEL = self.LABEL + '/' + encoding_type
        self.LABEL = self.LABEL + '/' + 'z3' + '/'
        
        # Define the paths of the results
        self.OUT_DIRECTORY = 'SAT/out/' + self.LABEL
        self.IMG_DIRECTORY = 'SAT/img/' + self.LABEL
        self.STAT_DIRECTORY = 'SAT/stats/' + self.LABEL
        
        # Create the directories
        os.makedirs(self.OUT_DIRECTORY, exist_ok=True)
        os.makedirs(self.IMG_DIRECTORY, exist_ok=True)
        os.makedirs(self.STAT_DIRECTORY, exist_ok=True)

    def execute(self):
        STAT_FILE_PATH = f'{self.STAT_DIRECTORY}data.csv'
        for instance_number in self.instances:
            IMG_FILE_PATH = f'{self.IMG_DIRECTORY}device-{str(instance_number)}.png'
            OUT_FILE_PATH = f'{self.OUT_DIRECTORY}solution-{str(instance_number)}.txt'
            
            if self.verbose:
                print(f'-----------------------------------------')
                print(f'[Instance number: {str(instance_number)}]')

            stats = utils.load_stats(STAT_FILE_PATH)

            key = 'ins-' + str(instance_number)
            if stats.loc[key]['height'] == '-' or self.OVERRIDE:
                if self.verbose:
                    print('Computing solution...')

                self.solve(self.model_name, instance_number, OUT_FILE_PATH, IMG_FILE_PATH, STAT_FILE_PATH)
            else:
                if self.verbose:
                    print('Solution already exists...')
                    print(f'-- Time required: {stats.at[key, "time"]} seconds')
            
            if self.verbose:
                print(f'-----------------------------------------')

        return STAT_FILE_PATH

    def solve(self, model_name, i, OUT_FILE_PATH, IMG_FILE_PATH, STAT_FILE_PATH):
        # Load instance
        plate_width, n_chips, chips_widths, chips_heights = utils.load_data(i)

        # Solve instance
        solver = self.MODEL_names[model_name](plate_width, 
                                              n_chips, 
                                              chips_widths, 
                                              chips_heights, 
                                              rotation = self.rotation_allowed, 
                                              symmetry_breaking = self.symmetry_required,
                                              encoding_type = self.encoding_type,
                                              time_available = self.TIME_AVAILABLE,
                                              interrupt = self.interrupt)

        # Set timeout and verify the satisfability of the model
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        p = multiprocessing.Process(target=solver.solve, args=(1, return_dict, self.verbose))
        p.start()
        p.join(self.TIME_AVAILABLE)
        if p.is_alive():
            p.terminate()
            p.join()
        
        # Get result
        is_solved = return_dict.values()[0]
        
        # The model is satisfable...
        if is_solved:
            # Evaluate the solution
            solving_time = return_dict['solving_time']
            pos_x = return_dict['pos_x']
            pos_y = return_dict['pos_y']
            chips_w_a = return_dict['chips_w_a']
            chips_h_a = return_dict['chips_h_a']
            plate_width = return_dict['plate_width']
            plate_height = return_dict['plate_height']
            rotation = return_dict['rotation']

            # Save image
            print(IMG_FILE_PATH)
            if self.print_img:
                utils.plot_device(pos_x, pos_y, chips_w_a, chips_h_a, plate_width, plate_height, rotation, IMG_FILE_PATH)

            # Save result
            utils.write_sol(OUT_FILE_PATH, 
                            plate_width, 
                            plate_height, 
                            n_chips, 
                            chips_widths, 
                            chips_heights, 
                            pos_x, 
                            pos_y,
                            rotation)

        else: # The model is not satisfable...
            plate_height, solving_time = solver.getSolutionUnsolved()
            
        utils.write_stat_line(STAT_FILE_PATH,
                              i,
                              plate_height,
                              solving_time, 
                              return_dict['result']) 
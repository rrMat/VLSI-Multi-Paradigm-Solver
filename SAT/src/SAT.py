from z3 import *
import math
import numpy as np 
import time
import utils.utils as utils

from SAT.src.SATModel import SATModel
import SAT.src.sat_utils as sat_utils

class SAT:

    MODELS = {
        'SATModel': SATModel
    }

    def __init__(self, model, rotation_allowed, symmetry_required, encoding_type, 
                       number_of_instances, time_available, interrupt, verbose, out_directory_path, 
                       img_directory_path, stats_directory_path, OVERRIDE):
        
        self.model = model
        self.rotation_allowed = rotation_allowed
        self.symmetry_required = symmetry_required
        self.encoding_type = encoding_type
        self.number_of_instances = number_of_instances
        self.time_available = time_available
        self.interrupt = interrupt
        self.verbose = verbose
        self.OVERRIDE = OVERRIDE

        self.label = self.model + ('_rot_' if self.rotation_allowed else '_not_rot_') + ('sb_' if self.symmetry_required else 'not_sb_') + self.encoding_type
        self.OUTS_DIRECTORY = out_directory_path + self.label + '/'
        self.IMGS_DIRECTORY = img_directory_path + self.label + '/'
        self.STATS_DIRECTORY = stats_directory_path
        
        os.makedirs(self.OUTS_DIRECTORY, exist_ok=True)
        os.makedirs(self.IMGS_DIRECTORY, exist_ok=True)


    def execute(self):
        STATS_FILE_PATH = self.STATS_DIRECTORY + self.label + '.csv'
        for instance_number in range(1, self.number_of_instances + 1):
            OUT_FILE_PATH = self.OUTS_DIRECTORY + str(instance_number) + '.txt'
            IMG_FILE_PATH = self.IMGS_DIRECTORY + str(instance_number) + '.jpg'
            
            if self.verbose:
                print(f'Instance number: {str(instance_number)}')

            stats = utils.load_stats(STATS_FILE_PATH)
            if (instance_number) not in stats.index or self.OVERRIDE:
                if self.verbose:
                    print('- Computing solution...')

                self.solve(self.model, instance_number, OUT_FILE_PATH, IMG_FILE_PATH, STATS_FILE_PATH)
            else:
                if self.verbose:
                    print('- Solution already exists...')
                    print(f'-- Time required: {stats.at[instance_number, "time"]} seconds')
              

    def solve(self, model, i, OUT_FILE_PATH, IMG_FILE_PATH, STATS_FILE_PATH):
        # Load instance
        plate_width, n_chips, chips_widths, chips_heights = utils.load_data(i)

        # Solve instance
        solver = self.MODELS[model](plate_width, 
                                    n_chips, 
                                    chips_widths, 
                                    chips_heights, 
                                    rotation = self.rotation_allowed, 
                                    symmetry_breaking = self.symmetry_required,
                                    encoding_type = self.encoding_type,
                                    time_available = self.time_available,
                                    interrupt = self.interrupt)
        is_solved = solver.solve()
        
        if is_solved:
            # Evaluate the solution
            pos_x, pos_y, chips_w_a, chips_h_a, plate_width, plate_min_height, plate_height, solving_time = solver.get_solution_solved_parsed()
            
            # Save results
            utils.plot_device(pos_x, pos_y, chips_w_a, chips_h_a, plate_width, plate_height, IMG_FILE_PATH)
            utils.write_sol(OUT_FILE_PATH, 
                            plate_width, 
                            plate_height, 
                            n_chips, 
                            chips_widths, 
                            chips_heights, 
                            pos_x, 
                            pos_y)
        else:
            plate_height, plate_min_height, solving_time = solver.get_solution_unsolved_parsed()
            
        utils.write_stat_line(STATS_FILE_PATH,
                              i,
                              plate_height,
                              plate_min_height,
                              solving_time) 
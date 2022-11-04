from itertools import combinations
import math
import time
import os
from tqdm import tqdm
import numpy as np
import sys
import VLSISolver
import sat_utils
import utils.utils as utils

OVERRIDE = True
INTERRUPT = True
PRINT = False
NUMBER_OF_INSTANCES = 40
TIME_AVAILABLE = 300


def solve(rotation, symmetry_breaking, encoding_type):

    NAME = ('rot_' if rotation else 'not_rot_') + ('sb_' if symmetry_breaking else 'not_sb_') + encoding_type

    OUT_DIRECTORY_PATH = '../out/' + NAME + '/'
    IMG_DIRECTORY_PATH = '../img/' + NAME + '/'
    STATS_PATH = '../stats/' + NAME + '.csv'

    os.makedirs(OUT_DIRECTORY_PATH, exist_ok=True)
    os.makedirs(IMG_DIRECTORY_PATH, exist_ok=True)
    
    for i in range(NUMBER_OF_INSTANCES):

        OUT_FILE_PATH = OUT_DIRECTORY_PATH + str(i+1) + '.txt'
        IMG_FILE_PATH = IMG_DIRECTORY_PATH + str(i+1) + '.jpg'
        
        if PRINT:
            print(f'Instance number: {str(i)}')

        stats = utils.load_stats(STATS_PATH)
        if i not in stats.index or OVERRIDE:

            print('- Computing solution...')
            # Load instance
            plate_width, n_chips, chips_widths, chips_heights = utils.load_data(i + 1)

            # Solve instance
            vlsi_solver = VLSISolver(plate_width, 
                                    n_chips, 
                                    chips_widths, 
                                    chips_heights, 
                                    rotation = rotation, 
                                    symmetry_breaking = symmetry_breaking,
                                    encoding_type=encoding_type,
                                    time_available = TIME_AVAILABLE,
                                    interrupt = INTERRUPT)
            is_solved = vlsi_solver.solve()
            
            # Print results
            if PRINT:
                print(f'-- Problem solved? {is_solved}')
                print(f'-- Time required: {vlsi_solver.solving_time} seconds')

            if is_solved:

                # Evaluate the solution
                pos_x, pos_y, chips_w_a, chips_h_a, plate_width, plate_height, solving_time = vlsi_solver.evalutate()
                
                # Print solution
                if PRINT:
                    utils.plot_device(pos_x, pos_y, chips_w_a, chips_h_a, plate_width, plate_height)
                
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
                utils.write_stat_line(STATS_PATH, 
                                      i + 1, 
                                      solving_time)
            
            else:
                utils.write_time_exceeded(OUT_FILE_PATH)
                utils.write_stat_line(STATS_PATH,
                                    i + 1,
                                    TIME_AVAILABLE)


        else:
            if PRINT:
                print('- Loading solution...')

            # Load results
            try:
                plate_width, plate_height, n_chips, chips_w_a, chips_h_a, pos_x, pos_y = utils.load_sol(OUT_FILE_PATH)
                stats = utils.load_stats(STATS_PATH)
            
                # Print result
                if PRINT:
                    print(f'-- Time required: {stats.at[i, "time"]} seconds')
                
                # Print solution
                if PRINT:
                    utils.plot_device(pos_x, pos_y, chips_w_a, chips_h_a, plate_width, plate_height)
            except OSError:
                print(f'-- Time exceeded!')
                
            
    utils.display_times(STATS_PATH)     
    return STATS_PATH       

            

